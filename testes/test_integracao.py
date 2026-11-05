"""Testa Flask com MySQL REAL em um banco exclusivo com sufixo _teste.

Executar explicitamente com GS_TEST_MYSQL=1. Não usa o banco do mural.
Antes, crie o banco de teste e dê acesso ao mesmo usuário, conforme o README.
"""
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
import mysql.connector
from elas.configuracao import carregar_configuracao
from elas.aplicacao import criar_app
from elas.banco import Repositorio
from receptor_tcp import criar_servidor
from testes.test_validacao import exemplo


@unittest.skipUnless(os.getenv('GS_TEST_MYSQL')=='1','Integração MySQL exige GS_TEST_MYSQL=1.')
class TestIntegracao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=carregar_configuracao()
        cls.config['DB_NAME']=cls.config['DB_NAME']+'_teste'
        if not cls.config['DB_NAME'].endswith('_teste'): raise RuntimeError('Banco de teste obrigatório')
        cls.temp=tempfile.TemporaryDirectory()
        cls.config.update(LOG_DIR=Path(cls.temp.name),TESTING=True,RATE_LIMIT=1000)
        cls.repo=Repositorio(cls.config); cls.repo.inicializar()
        cls.tcp=criar_servidor(cls.config,('127.0.0.1',0))
        cls.config['TCP_PORT']=cls.tcp.server_address[1]
        cls.th=threading.Thread(target=cls.tcp.serve_forever,daemon=True); cls.th.start()

    @classmethod
    def tearDownClass(cls):
        cls.tcp.shutdown(); cls.tcp.server_close(); cls.th.join()
        import logging
        for nome,logger in list(logging.Logger.manager.loggerDict.items()):
            if isinstance(logger,logging.Logger) and cls.temp.name in nome:
                for h in logger.handlers[:]: h.close(); logger.removeHandler(h)
        cls.temp.cleanup()

    def setUp(self):
        # Só o banco com sufixo _teste é limpo. A proteção está em setUpClass.
        with self.repo.conexao() as c:
            with c.cursor() as cur:
                cur.execute('DELETE FROM notificacoes'); cur.execute('DELETE FROM anuncios')
            c.commit()
        self.app=criar_app(self.config,self.repo)
        self.client=self.app.test_client()
        self.auth={'X-API-Key':self.config['API_KEY']}

    def criar(self,**mudancas):
        r=self.client.post('/api/anuncios',json=exemplo(**mudancas),headers=self.auth)
        self.assertEqual(r.status_code,201,r.get_json())
        return r.get_json()['item']

    def test_crud_completo_mysql_e_status(self):
        item=self.criar(); ident=item['id']
        self.assertEqual(self.client.get(f'/api/anuncios/{ident}').status_code,200)
        r=self.client.put(f'/api/anuncios/{ident}',json=exemplo(versao=1,status='concluido'),headers=self.auth)
        self.assertEqual(r.status_code,200); self.assertEqual(r.json['item']['versao'],2)
        self.assertEqual(self.repo.obter(ident)['status'],'concluido')
        r=self.client.delete(f'/api/anuncios/{ident}',headers=self.auth)
        self.assertEqual(r.status_code,204); self.assertEqual(r.data,b'')
        self.assertEqual(self.client.get(f'/api/anuncios/{ident}').status_code,404)

    def test_escrita_sem_chave_e_com_chave_errada(self):
        for headers in ({},{'X-API-Key':'incorreta'},{'X-API-Key':'inválida'}):
            self.assertEqual(self.client.post('/api/anuncios',json=exemplo(),headers=headers).status_code,401)
        self.assertEqual(self.repo.resumo()['total'],0)

    def test_bloqueia_origem_cruzada(self):
        r=self.client.post('/api/anuncios',json=exemplo(),headers=dict(self.auth,Origin='https://outra-origem.test'))
        self.assertEqual(r.status_code,403)

    def test_sql_injection_permanece_texto(self):
        titulo="Livro'; DROP TABLE anuncios; --"
        item=self.criar(titulo=titulo)
        self.assertEqual(self.repo.obter(item['id'])['titulo'],titulo)
        r=self.client.get('/api/anuncios',query_string={'busca':"' OR 1=1 --"})
        self.assertEqual(r.status_code,200); self.assertEqual(r.json['total'],0)

    def test_validacao_xss_e_municipio(self):
        for dados in (exemplo(titulo='<script>alert(1)</script>'),exemplo(municipio_id=9999999)):
            self.assertEqual(self.client.post('/api/anuncios',json=dados,headers=self.auth).status_code,400)

    def test_versao_evitar_perda_de_edicao(self):
        item=self.criar(); url='/api/anuncios/'+str(item['id'])
        self.assertEqual(self.client.put(url,json=exemplo(versao=1,status='reservado'),headers=self.auth).status_code,200)
        self.assertEqual(self.client.put(url,json=exemplo(versao=1),headers=self.auth).status_code,409)
        self.assertEqual(self.repo.obter(item['id'])['status'],'reservado')

    def test_tcp_indisponivel_nao_perde_anuncio_e_reenvia(self):
        with patch('elas.notificacoes.enviar_aviso',return_value=False):
            item=self.criar()
        self.assertIsNotNone(self.repo.obter(item['id']))
        self.assertEqual(len(self.repo.pendentes()),1)
        r=self.client.post('/api/notificacoes/reenviar',headers=self.auth)
        self.assertEqual(r.json['entregues'],1); self.assertEqual(self.repo.pendentes(),[])

    def test_conexoes_usam_categoria_cidade_e_situacao(self):
        item=self.criar(tipo='pedido')
        certo=self.criar()
        self.criar(status='concluido'); self.criar(municipio_id=3550308); self.criar(categoria='aprendizagem')
        r=self.client.get('/api/conexoes/'+str(item['id']))
        self.assertEqual([x['id'] for x in r.json['items']],[certo['id']])

    def test_limite_corpo_json_e_tipo_conteudo(self):
        self.assertEqual(self.client.post('/api/anuncios',data='a'*17000,content_type='application/json',headers=self.auth).status_code,413)
        self.assertEqual(self.client.post('/api/anuncios',data='texto',headers=self.auth).status_code,415)
        self.assertEqual(self.client.post('/api/anuncios',data='{',content_type='application/json',headers=self.auth).status_code,400)

    def test_erros_sem_detalhes_do_banco(self):
        with patch.object(self.repo,'listar',side_effect=mysql.connector.Error('senha-interna-secreta')):
            r=self.client.get('/api/anuncios')
        self.assertEqual(r.status_code,503); self.assertNotIn(b'senha-interna',r.data)

    def test_logs_nao_contem_chaves_ou_descricao(self):
        self.criar(descricao='Descricao exclusiva para verificar minimizacao no log.')
        conteudo=(Path(self.temp.name)/'aplicacao.log').read_text(encoding='utf-8')
        self.assertIn('anuncio_criar',conteudo)
        self.assertNotIn(self.config['API_KEY'],conteudo)
        self.assertNotIn('Descricao exclusiva',conteudo)

    def test_cabecalhos_e_metodo_nao_permitido(self):
        r=self.client.get('/')
        self.assertEqual(r.status_code,200)
        self.assertIn("frame-ancestors 'none'",r.headers['Content-Security-Policy'])
        self.assertEqual(self.client.patch('/api/anuncios').status_code,405)

    def test_filtros_invalidos_e_repetidos(self):
        for q in ('tipo=outro','pagina=-1','tipo=pedido&tipo=doacao','campo=extra','municipio_id=abc'):
            self.assertEqual(self.client.get('/api/anuncios?'+q).status_code,400)

    def test_rate_limit(self):
        cfg=dict(self.config,RATE_LIMIT=2)
        client=criar_app(cfg,self.repo).test_client()
        self.assertEqual(client.get('/api/resumo').status_code,200)
        self.assertEqual(client.get('/api/resumo').status_code,200)
        self.assertEqual(client.get('/api/resumo').status_code,429)
