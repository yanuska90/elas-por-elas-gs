"""Diagnóstico municipal com SQL direto, geografia pública e evidência separada.

Não estima população, pobreza, criminalidade ou representatividade estatística.
Um registro é uma necessidade cadastrada pela gestão, não uma pessoa atendida.
"""
import json
import math
from datetime import datetime, timezone
from urllib.parse import urlsplit
import requests
from .catalogo import SETORES
from .validacao import texto, inteiro, ErroValidacao
from .banco import Repositorio, ConflitoEdicao
from .configuracao import RAIZ
from .localidades import FonteIndisponivel

NATUREZAS={'simulado','dado_publico'}
SITUACOES={'registrada','em_analise','encaminhada','concluida'}

def validar_necessidade(dados, edicao=False):
    campos={'municipio_id','setor','titulo','descricao','prioridade','natureza','fonte_url','status'}
    if edicao: campos.add('versao')
    if not isinstance(dados,dict) or set(dados)!=campos:
        raise ErroValidacao('Informe somente os campos previstos para a necessidade.')
    for k,opcoes in [('setor',SETORES),('natureza',NATUREZAS),('status',SITUACOES)]:
        if not isinstance(dados[k],str) or dados[k] not in opcoes:
            raise ErroValidacao(f'{k}: opção inválida.')
    d={k:dados[k] for k in ('setor','natureza','status')}
    d.update(municipio_id=inteiro(dados['municipio_id'],'Município',1000000,9999999),
             prioridade=inteiro(dados['prioridade'],'Prioridade',1,3),
             titulo=texto(dados['titulo'],'Título',5,100),
             descricao=texto(dados['descricao'],'Descrição',15,800))
    fonte=dados['fonte_url']
    if not isinstance(fonte,str) or len(fonte)>300:
        raise ErroValidacao('Fonte inválida.')
    if d['natureza']=='dado_publico':
        try:
            url=urlsplit(fonte)
            porta=url.port
        except ValueError: raise ErroValidacao('Endereço da fonte inválido.')
        dominio=(url.hostname or '').lower()
        if url.scheme!='https' or not (dominio.endswith('.gov.br') or dominio=='gov.br') or url.username or url.password or porta not in (None,443) or url.query or url.fragment:
            raise ErroValidacao('Use URL HTTPS de fonte governamental, sem credenciais, consulta ou fragmento.')
    elif fonte:
        raise ErroValidacao('Exemplos simulados não devem aparentar evidência pública.')
    d['fonte_url']=fonte
    if edicao: d['versao']=inteiro(dados['versao'],'Versão')
    return d

def filtros_territorio(args):
    if set(args)-{'municipio_id','setor','natureza'} or any(len(args.getlist(k))!=1 for k in args):
        raise ErroValidacao('Filtro territorial inválido ou repetido.')
    d={'natureza':args.get('natureza','simulado')}
    if d['natureza'] not in NATUREZAS: raise ErroValidacao('Natureza inválida.')
    if args.get('setor'):
        if args['setor'] not in SETORES: raise ErroValidacao('Setor inválido.')
        d['setor']=args['setor']
    if args.get('municipio_id'):
        if not args['municipio_id'].isascii() or not args['municipio_id'].isdigit(): raise ErroValidacao('Município inválido.')
        d['municipio_id']=inteiro(int(args['municipio_id']),'Município',1000000,9999999)
    return d

class Territorio:
    def __init__(self, repo): self.repo=repo

    def listar(self,filtros):
        partes=[]; valores=[]
        for campo in ('municipio_id','setor','natureza'):
            if campo in filtros:
                partes.append('n.'+campo+'=%s'); valores.append(filtros[campo])
        with self.repo.conexao() as c, c.cursor(dictionary=True) as cur:
            cur.execute('SELECT n.*,m.nome AS municipio,m.uf FROM necessidades n JOIN municipios m ON m.id=n.municipio_id WHERE '+ ' AND '.join(partes)+' ORDER BY n.prioridade DESC,n.id DESC LIMIT 1001',valores)
            itens=[Repositorio.serializar(i) for i in cur.fetchall()]
        return {'items':itens[:1000],'truncado':len(itens)>1000,'limite':1000}

    def obter(self,ident):
        with self.repo.conexao() as c, c.cursor(dictionary=True) as cur:
            cur.execute('SELECT n.*,m.nome AS municipio,m.uf FROM necessidades n JOIN municipios m ON m.id=n.municipio_id WHERE n.id=%s',(ident,))
            return Repositorio.serializar(cur.fetchone())

    def salvar(self,d,ident=None):
        campos=('municipio_id','setor','titulo','descricao','prioridade','natureza','fonte_url','status')
        valores=tuple(d[k] for k in campos)
        with self.repo.conexao() as c, c.cursor() as cur:
            if ident is None:
                cur.execute('INSERT INTO necessidades (municipio_id,setor,titulo,descricao,prioridade,natureza,fonte_url,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',valores)
                ident=cur.lastrowid
            else:
                cur.execute('SELECT versao FROM necessidades WHERE id=%s FOR UPDATE',(ident,))
                atual=cur.fetchone()
                if not atual: return None
                if atual[0]!=d['versao']: raise ConflitoEdicao()
                cur.execute('UPDATE necessidades SET municipio_id=%s,setor=%s,titulo=%s,descricao=%s,prioridade=%s,natureza=%s,fonte_url=%s,status=%s,versao=versao+1,atualizado_em=UTC_TIMESTAMP() WHERE id=%s',valores+(ident,))
            c.commit()
        return ident

    def excluir(self,ident):
        with self.repo.conexao() as c, c.cursor() as cur:
            cur.execute('DELETE FROM necessidades WHERE id=%s',(ident,)); achou=cur.rowcount
            c.commit()
        return bool(achou)

    def salvar_regiao(self,ident,d):
        with self.repo.conexao() as c, c.cursor() as cur:
            cur.execute('INSERT INTO regioes (municipio_id,latitude,longitude,geometria,fonte,consultado_em) VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE latitude=VALUES(latitude),longitude=VALUES(longitude),geometria=VALUES(geometria),fonte=VALUES(fonte),consultado_em=VALUES(consultado_em)',
                        (ident,d['latitude'],d['longitude'],json.dumps(d['geometria']),d['fonte'],datetime.fromisoformat(d['consultado_em'].replace('Z','+00:00')).replace(tzinfo=None)))
            c.commit()

    def regioes(self):
        with self.repo.conexao() as c, c.cursor(dictionary=True) as cur:
            cur.execute('SELECT r.*,m.nome AS municipio,m.uf FROM regioes r JOIN municipios m ON m.id=r.municipio_id ORDER BY m.nome')
            resultado=[]
            for r in cur.fetchall():
                r=Repositorio.serializar(r); r['geometria']=json.loads(r['geometria']); resultado.append(r)
            return resultado

    def relatorio(self,filtros):
        fonte=self.listar(filtros); grupos={}
        for item in fonte['items']:
            k=(item['municipio_id'],item['setor'])
            g=grupos.setdefault(k,{'municipio_id':k[0],'municipio':item['municipio'],'uf':item['uf'],'setor':k[1],
                                  'ods':SETORES[k[1]][1],'registros':0,'pendentes':0,'alta_prioridade':0,
                                  'proposta_inicial':SETORES[k[1]][2],'fontes':set()})
            g['registros']+=1; g['pendentes']+=item['status']!='concluida'; g['alta_prioridade']+=item['prioridade']==3 and item['status']!='concluida'
            if item['fonte_url']: g['fontes'].add(item['fonte_url'])
        for g in grupos.values(): g['fontes']=sorted(g['fontes'])
        return {'gerado_em':datetime.now(timezone.utc).isoformat(),'natureza':filtros['natureza'],
                'filtros':filtros,'truncado':fonte['truncado'],'registros_considerados':len(fonte['items']),
                'metodologia':'Contagem de registros cadastrados; prioridade de 1 a 3 atribuída pela gestão. Não representa número de pessoas, pesquisa amostral ou carência comprovada. Fontes públicas cadastradas não são verificadas automaticamente.',
                'uso':'Minuta para revisão humana antes de solicitar projetos públicos. Não é protocolo nem envio ao governo.',
                'proximos_passos':['Validar evidências e abrangência territorial com a comunidade.','Consultar dados oficiais e verificar duplicidades.','Definir órgão competente, orçamento e responsáveis.','Revisar a minuta e protocolar no canal oficial apropriado.'],
                'grupos':sorted(grupos.values(),key=lambda g:(-g['alta_prioridade'],-g['pendentes'],g['municipio']))}

def extrair_geografia(payload,ident):
    """Lê GeoJSON do IBGE e deriva somente um ponto aproximado para o mapa."""
    try:
        fs=payload['features']
        if not isinstance(fs,list) or not 1<=len(fs)<=30: raise ValueError()
        geometrias=[]; pontos=[]
        def visitar(v,nivel=0):
            if nivel>7 or not isinstance(v,list): raise ValueError()
            if len(v)>=2 and all(type(x) in (int,float) for x in v[:2]):
                x,y=v[:2]
                if not math.isfinite(x) or not math.isfinite(y) or not (-180<=x<=180 and -90<=y<=90): raise ValueError()
                pontos.append((x,y)); return
            for filho in v: visitar(filho,nivel+1)
        for f in fs:
            g=f['geometry']
            if g['type'] not in {'Polygon','MultiPolygon'}: raise ValueError()
            visitar(g['coordinates']); geometrias.append({'type':g['type'],'coordinates':g['coordinates']})
        if not pontos: raise ValueError()
        return {'latitude':round((min(y for x,y in pontos)+max(y for x,y in pontos))/2,6),
                'longitude':round((min(x for x,y in pontos)+max(x for x,y in pontos))/2,6),
                'geometria':{'type':'GeometryCollection','geometries':geometrias},
                'fonte':f'https://servicodados.ibge.gov.br/api/v3/malhas/municipios/{ident}',
                'consultado_em':datetime.now(timezone.utc).isoformat()}
    except (KeyError,TypeError,ValueError): raise FonteIndisponivel('Malha inválida')

def localizar_municipio(ident,territorio):
    salvo=next((r for r in territorio.regioes() if r['municipio_id']==ident),None)
    if salvo:
        idade=datetime.now(timezone.utc)-datetime.fromisoformat(salvo['consultado_em'].replace('Z','+00:00'))
        if idade.total_seconds()<86400: return dict(salvo,origem='cache_mysql',desatualizado=False)
    try:
        url=f'https://servicodados.ibge.gov.br/api/v3/malhas/municipios/{ident}'
        with requests.get(url,params={'formato':'application/vnd.geo+json','qualidade':'minima'},headers={'Accept':'application/vnd.geo+json','User-Agent':'ElasPorElasAcademico/2.0'},timeout=(3,8),stream=True,allow_redirects=False) as r:
            r.raise_for_status()
            if r.status_code!=200: raise ValueError()
            partes=[]; total=0
            for bloco in r.iter_content(16384):
                total+=len(bloco)
                if total>2000000: raise ValueError()
                partes.append(bloco)
        d=extrair_geografia(json.loads(b''.join(partes)),ident)
        territorio.salvar_regiao(ident,d)
        return dict(d,municipio_id=ident,origem='api_ibge',desatualizado=False)
    except (requests.RequestException,ValueError,FonteIndisponivel):
        if salvo: return dict(salvo,origem='cache_mysql',desatualizado=True)
        snapshot=RAIZ/'dados/geografia_municipal.json'
        if snapshot.exists():
            d=json.loads(snapshot.read_text(encoding='utf-8')).get(str(ident))
            if d:
                territorio.salvar_regiao(ident,d)
                return dict(d,municipio_id=ident,origem='snapshot_publico',desatualizado=True)
        raise FonteIndisponivel('Não há geografia disponível para este município.')
