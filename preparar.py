"""Cria .env com segredos únicos. Nunca sobrescreve uma configuração existente."""
import secrets
from pathlib import Path


def preparar():
    raiz = Path(__file__).resolve().parent
    for pasta in ('logs', 'dados/cache'):
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    destino = raiz / '.env'
    if destino.exists():
        print('.env já existe. Configuração preservada.')
        return
    texto = (raiz / '.env.example').read_text(encoding='utf-8')
    linhas = []
    for linha in texto.splitlines():
        if '=SUBSTITUA_' in linha:
            linha = linha.split('=',1)[0] + '=' + secrets.token_hex(32)
        linhas.append(linha)
    with destino.open('x', encoding='utf-8') as arquivo:
        arquivo.write('\n'.join(linhas) + '\n')
    try:
        destino.chmod(0o600)
    except OSError:
        pass
    print('Configuração criada. Os segredos ficaram somente no .env local.')


if __name__ == '__main__':
    preparar()
