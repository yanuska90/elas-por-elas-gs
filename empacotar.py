"""Gera o ZIP acadêmico sem configurações privadas ou arquivos de execução.

Yanuska Monalisa Antunes Yabiku - RM 571686.
Usa somente a biblioteca padrão. Execute novamente depois de incluir prints.
"""
from pathlib import Path
from hashlib import sha256
import json
import zipfile

RAIZ = Path(__file__).resolve().parent
PASTAS = {'elas', 'sql', 'static', 'visao', 'testes', 'dados', 'documentacao', 'evidencias'}
RAIZ_PERMITIDOS = {
    'README.md', 'requirements.txt', '.env.example', '.gitignore', '.dockerignore',
    'Dockerfile', 'compose.yaml', 'iniciar.ps1', 'preparar.py', 'preparar_testes.py',
    'servidor.py', 'receptor_tcp.py', 'povoar_exemplos.py', 'verificar.py', 'empacotar.py'
}
EXTENSOES = {'.py', '.sql', '.html', '.css', '.js', '.svg', '.json', '.jsonl', '.md', '.pdf', '.jpg', '.jpeg', '.png'}


def selecionar():
    """Uma lista positiva evita levar ambientes, caches ou arquivos pessoais."""
    resultado = []
    for arquivo in sorted(RAIZ.rglob('*')):
        if not arquivo.is_file() or arquivo.is_symlink():
            continue
        relativo = arquivo.relative_to(RAIZ)
        if any(p in {'__pycache__', '.git', '.venv', 'cache', 'temporarios'} for p in relativo.parts):
            continue
        if len(relativo.parts) == 1:
            aceito = arquivo.name in RAIZ_PERMITIDOS
        else:
            aceito = relativo.parts[0] in PASTAS and arquivo.suffix.lower() in EXTENSOES
        if not aceito:
            continue
        if any(p.lower().startswith('.env') and p != '.env.example' for p in relativo.parts):
            raise ValueError('Configuração privada selecionada indevidamente.')
        if any(x in str(relativo).lower() for x in ('codex', 'chatgpt', 'chat gpt')):
            raise ValueError('Nome de arquivo incompatível com a organização da entrega.')
        resultado.append(arquivo)
    return resultado


def segredos_locais():
    """Lê apenas para comparar; os valores nunca são impressos ou exportados."""
    env = RAIZ / '.env'
    if not env.exists():
        return []
    nomes = {'API_KEY', 'TCP_TOKEN', 'DB_PASSWORD', 'MYSQL_ROOT_PASSWORD'}
    valores = []
    for linha in env.read_text(encoding='utf-8-sig').splitlines():
        chave, separador, valor = linha.partition('=')
        if separador and chave.strip() in nomes and len(valor.strip()) >= 16:
            valores.append(valor.strip().encode('utf-8'))
    return valores


def empacotar():
    arquivos = selecionar()
    segredos = segredos_locais()
    manifesto = {}
    for arquivo in arquivos:
        conteudo = arquivo.read_bytes()
        if any(segredo in conteudo for segredo in segredos):
            raise ValueError('Um arquivo selecionado contém um segredo local; revise antes da entrega.')
        manifesto[arquivo.relative_to(RAIZ).as_posix()] = sha256(conteudo).hexdigest()
    destino = RAIZ.parent / 'GS_Elas_por_Elas_Yanuska_RM571686.zip'
    # O manifesto não inclui a si mesmo: identifica exatamente os demais arquivos.
    with zipfile.ZipFile(destino, 'w', compression=zipfile.ZIP_DEFLATED) as pacote:
        for arquivo in arquivos:
            pacote.write(arquivo, 'Elas por Elas/' + arquivo.relative_to(RAIZ).as_posix())
        pacote.writestr('Elas por Elas/MANIFESTO_SHA256.json', json.dumps(manifesto, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(destino) as pacote:
        if pacote.testzip() is not None:
            raise ValueError('Falha na verificação de integridade do ZIP.')
    print(f'ZIP verificado: {destino.name}; {len(arquivos)} arquivos e manifesto.')
    return destino


if __name__ == '__main__':
    empacotar()
