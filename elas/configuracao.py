"""Carrega os segredos do ambiente; o código não contém senhas prontas."""
import os
from pathlib import Path
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[1]


def carregar_configuracao():
    # Variáveis definidas pelo Docker têm prioridade sobre o .env local.
    load_dotenv(RAIZ / '.env', override=False)
    for nome in ('API_KEY', 'TCP_TOKEN', 'DB_PASSWORD'):
        valor = os.getenv(nome, '')
        if len(valor) < 24 or valor.startswith('SUBSTITUA'):
            raise ValueError('Configure os segredos com: python preparar.py')
    return {
        'DB_HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'DB_PORT': int(os.getenv('DB_PORT', '3308')),
        'DB_NAME': os.getenv('DB_NAME', 'elas_por_elas'),
        'DB_USER': os.getenv('DB_USER', 'elas_app'),
        'DB_PASSWORD': os.environ['DB_PASSWORD'],
        'API_KEY': os.environ['API_KEY'],
        'TCP_TOKEN': os.environ['TCP_TOKEN'],
        'TCP_HOST': os.getenv('TCP_HOST', '127.0.0.1'),
        'TCP_BIND': os.getenv('TCP_BIND', '127.0.0.1'),
        'TCP_PORT': int(os.getenv('TCP_PORT', '19088')),
        'APP_HOST': os.getenv('APP_HOST', '127.0.0.1'),
        'APP_PORT': int(os.getenv('APP_PORT', '5055')),
        'CACHE_TTL_HOURS': int(os.getenv('CACHE_TTL_HOURS', '24')),
        'CACHE_DIR': RAIZ / 'dados' / 'cache',
        'LOG_DIR': RAIZ / 'logs',
        'SNAPSHOT': RAIZ / 'dados' / 'municipios_sp.json',
        'MAX_CONTENT_LENGTH': 16384,
        'TESTING': False,
        'RATE_LIMIT': 90,
    }
