"""CRUD com MySQL Connector e SQL explícito, sem ORM.

Os valores recebidos nunca são concatenados ao SQL: execute recebe parâmetros
em separado. Os fragmentos dinâmicos abaixo são constantes internas permitidas.
"""
import json
import uuid
from contextlib import contextmanager
from datetime import datetime
import mysql.connector
from .configuracao import RAIZ


class ConflitoEdicao(Exception):
    """A versão foi alterada por outra janela. É necessário recarregar."""


class Repositorio:
    def __init__(self, config):
        self.config = config

    @contextmanager
    def conexao(self):
        c = mysql.connector.connect(
            host=self.config['DB_HOST'], port=self.config['DB_PORT'],
            user=self.config['DB_USER'], password=self.config['DB_PASSWORD'],
            database=self.config['DB_NAME'], connection_timeout=5,
            charset='utf8mb4', time_zone='+00:00', autocommit=False,
        )
        try:
            yield c
        except Exception:
            c.rollback()
            raise
        finally:
            c.close()

    def inicializar(self):
        # O arquivo SQL é parte do projeto, nunca enviado pelo visitante.
        comandos = (RAIZ / 'sql/esquema.sql').read_text(encoding='utf-8')
        with self.conexao() as c:
            with c.cursor() as cur:
                for comando in comandos.split(';'):
                    if comando.strip():
                        cur.execute(comando)
            c.commit()
        snapshot = json.loads(self.config['SNAPSHOT'].read_text(encoding='utf-8'))
        self.salvar_municipios(snapshot['items'])

    def salvar_municipios(self, itens):
        with self.conexao() as c:
            with c.cursor() as cur:
                cur.executemany(
                    'INSERT INTO municipios (id,nome,uf) VALUES (%s,%s,%s) '
                    'ON DUPLICATE KEY UPDATE nome=VALUES(nome),uf=VALUES(uf)',
                    [(i['id'], i['nome'], i['uf']) for i in itens])
            c.commit()

    def municipio_existe(self, municipio_id):
        with self.conexao() as c:
            with c.cursor() as cur:
                cur.execute('SELECT 1 FROM municipios WHERE id=%s', (municipio_id,))
                return cur.fetchone() is not None

    def municipios(self):
        with self.conexao() as c:
            with c.cursor(dictionary=True) as cur:
                cur.execute('SELECT id,nome,uf FROM municipios ORDER BY uf,nome')
                return cur.fetchall()

    @staticmethod
    def serializar(item):
        if not item:
            return None
        return {k: v.isoformat() + 'Z' if isinstance(v, datetime) else v
                for k, v in item.items()}

    def listar(self, filtros):
        condicoes, valores = [], []
        for campo in ('tipo', 'categoria', 'status', 'municipio_id'):
            if campo in filtros:
                condicoes.append('a.' + campo + '=%s')
                valores.append(filtros[campo])
        if filtros.get('busca'):
            # LOCATE procura texto literal: % e _ não se tornam curingas.
            condicoes.append('(LOCATE(%s,a.titulo)>0 OR LOCATE(%s,a.descricao)>0)')
            valores.extend([filtros['busca'], filtros['busca']])
        where = ' WHERE ' + ' AND '.join(condicoes) if condicoes else ''
        pagina, tamanho = filtros.get('pagina', 1), 12
        with self.conexao() as c:
            with c.cursor(dictionary=True) as cur:
                cur.execute('SELECT COUNT(*) AS total FROM anuncios a' + where, valores)
                total = cur.fetchone()['total']
                cur.execute('SELECT a.*,m.nome AS municipio,m.uf FROM anuncios a '
                            'JOIN municipios m ON m.id=a.municipio_id' + where +
                            ' ORDER BY a.id DESC LIMIT %s OFFSET %s',
                            valores + [tamanho, (pagina - 1) * tamanho])
                itens = [self.serializar(i) for i in cur.fetchall()]
        return {'items': itens, 'total': total, 'pagina': pagina, 'por_pagina': tamanho}

    def obter(self, anuncio_id):
        with self.conexao() as c:
            with c.cursor(dictionary=True) as cur:
                cur.execute('SELECT a.*,m.nome AS municipio,m.uf FROM anuncios a '
                            'JOIN municipios m ON m.id=a.municipio_id WHERE a.id=%s', (anuncio_id,))
                return self.serializar(cur.fetchone())

    @staticmethod
    def enfileirar(cur, anuncio_id, acao):
        aviso_id = str(uuid.uuid4())
        cur.execute('INSERT INTO notificacoes (id,anuncio_id,acao) VALUES (%s,%s,%s)',
                    (aviso_id, anuncio_id, acao))
        return aviso_id

    def criar(self, dados):
        with self.conexao() as c:
            with c.cursor() as cur:
                cur.execute('INSERT INTO anuncios '
                            '(titulo,tipo,categoria,descricao,contrapartida,municipio_id,status) '
                            'VALUES (%s,%s,%s,%s,%s,%s,%s)',
                            tuple(dados[k] for k in ('titulo','tipo','categoria','descricao',
                                                    'contrapartida','municipio_id','status')))
                anuncio_id = cur.lastrowid
                aviso_id = self.enfileirar(cur, anuncio_id, 'criar')
            c.commit()  # Somente após o COMMIT tentamos a comunicação externa.
        return anuncio_id, aviso_id

    def atualizar(self, anuncio_id, dados):
        with self.conexao() as c:
            with c.cursor() as cur:
                cur.execute('SELECT versao FROM anuncios WHERE id=%s FOR UPDATE', (anuncio_id,))
                atual = cur.fetchone()
                if not atual:
                    return None
                if atual[0] != dados['versao']:
                    raise ConflitoEdicao()
                cur.execute('UPDATE anuncios SET titulo=%s,tipo=%s,categoria=%s,descricao=%s,'
                            'contrapartida=%s,municipio_id=%s,status=%s,versao=versao+1,'
                            'atualizado_em=UTC_TIMESTAMP() WHERE id=%s',
                            tuple(dados[k] for k in ('titulo','tipo','categoria','descricao',
                                                    'contrapartida','municipio_id','status')) + (anuncio_id,))
                aviso_id = self.enfileirar(cur, anuncio_id, 'atualizar')
            c.commit()
        return aviso_id

    def excluir(self, anuncio_id):
        with self.conexao() as c:
            with c.cursor() as cur:
                cur.execute('DELETE FROM anuncios WHERE id=%s', (anuncio_id,))
                if not cur.rowcount:
                    return None
                aviso_id = self.enfileirar(cur, anuncio_id, 'excluir')
            c.commit()
        return aviso_id

    def resumo(self):
        with self.conexao() as c:
            with c.cursor(dictionary=True) as cur:
                cur.execute("SELECT COUNT(*) AS total,COALESCE(SUM(tipo='pedido'),0) AS pedidos,"
                            "COALESCE(SUM(status='concluido'),0) AS concluidos FROM anuncios")
                return {k: int(v) for k,v in cur.fetchone().items()}

    def pendentes(self, aviso_id=None):
        with self.conexao() as c:
            with c.cursor(dictionary=True) as cur:
                if aviso_id:
                    cur.execute('SELECT id,anuncio_id,acao FROM notificacoes '
                                'WHERE entregue_em IS NULL AND id=%s', (aviso_id,))
                else:
                    cur.execute('SELECT id,anuncio_id,acao FROM notificacoes '
                                'WHERE entregue_em IS NULL ORDER BY criado_em LIMIT 20')
                return cur.fetchall()

    def marcar_tentativa(self, aviso_id, sucesso):
        with self.conexao() as c:
            with c.cursor() as cur:
                cur.execute('UPDATE notificacoes SET tentativas=tentativas+1,'
                            'entregue_em=IF(%s,UTC_TIMESTAMP(),entregue_em) WHERE id=%s',
                            (sucesso, aviso_id))
            c.commit()
