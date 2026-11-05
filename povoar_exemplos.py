"""Insere demonstrações sem apagar registros. --complementar amplia a versão anterior."""
import argparse
import json
from datetime import datetime, timedelta, timezone
from elas.configuracao import RAIZ, carregar_configuracao
from elas.banco import Repositorio
from elas.auditoria import criar_logger
from elas.notificacoes import despachar
from elas.validacao import validar_anuncio
from elas.territorio import Territorio, validar_necessidade


def executar(complementar=False):
    config = carregar_configuracao()
    repo = Repositorio(config)
    repo.inicializar()
    if repo.resumo()['total'] and not complementar:
        print('Mural existente preservado. Use --complementar para incluir apenas exemplos novos.')
        return
    with repo.conexao() as c, c.cursor() as cur:
        cur.execute('SELECT titulo FROM anuncios'); titulos={r[0] for r in cur.fetchall()}
        cur.execute('SELECT titulo FROM necessidades'); demandas={r[0] for r in cur.fetchall()}
    exemplos = json.loads((RAIZ / 'dados/anuncios_exemplo.json').read_text(encoding='utf-8'))
    incluidos=0
    for exemplo in exemplos:
        if exemplo['titulo'] in titulos: continue
        horas=exemplo.pop('prazo_exemplo_horas',None)
        if horas:
            exemplo.setdefault('detalhes',{})['disponivel_ate']=(datetime.now(timezone.utc)+timedelta(hours=horas)).strftime('%Y-%m-%dT%H:%M:%SZ')
        dados = validar_anuncio(exemplo)
        if not repo.municipio_existe(dados['municipio_id']):
            raise ValueError('O município do exemplo não foi encontrado.')
        repo.criar(dados)
        incluidos+=1
    territorio=Territorio(repo); n=0
    for d in json.loads((RAIZ/'dados/necessidades_exemplo.json').read_text(encoding='utf-8')):
        if d['titulo'] not in demandas:
            territorio.salvar(validar_necessidade(d)); n+=1
    # Só preenche geografia ausente: não substitui consultas mais recentes.
    existentes={r['municipio_id'] for r in territorio.regioes()}
    snapshot=RAIZ/'dados/geografia_municipal.json'
    if snapshot.exists():
        for ident,d in json.loads(snapshot.read_text(encoding='utf-8')).items():
            if int(ident) not in existentes: territorio.salvar_regiao(int(ident),d)
    resultado = despachar(config, repo, criar_logger(config['LOG_DIR']))
    print(f"Incluídos {incluidos} anúncios e {n} necessidades fictícias; {resultado['entregues']} avisos confirmados. Registros anteriores preservados.")


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--complementar',action='store_true')
    executar(parser.parse_args().complementar)
