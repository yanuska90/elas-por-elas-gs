"""Insere exemplos fictícios somente em um banco vazio. Não apaga registros."""
import json
from elas.configuracao import RAIZ, carregar_configuracao
from elas.banco import Repositorio
from elas.auditoria import criar_logger
from elas.notificacoes import despachar
from elas.validacao import validar_anuncio


def executar():
    config = carregar_configuracao()
    repo = Repositorio(config)
    repo.inicializar()
    if repo.resumo()['total']:
        print('O mural já contém registros. Nenhum exemplo foi inserido.')
        return
    exemplos = json.loads((RAIZ / 'dados/anuncios_exemplo.json').read_text(encoding='utf-8'))
    for exemplo in exemplos:
        dados = validar_anuncio(exemplo)
        if not repo.municipio_existe(dados['municipio_id']):
            raise ValueError('O município do exemplo não foi encontrado.')
        repo.criar(dados)
    resultado = despachar(config, repo, criar_logger(config['LOG_DIR']))
    print(f"{len(exemplos)} exemplos fictícios inseridos; {resultado['entregues']} avisos confirmados.")


if __name__ == '__main__':
    executar()
