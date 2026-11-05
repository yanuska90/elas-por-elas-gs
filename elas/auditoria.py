"""Log JSON por linha: data UTC, ação, resultado e identificador técnico.

Não gravamos chave de API, texto do anúncio, telefone, cookie ou endereço IP.
O limite e a rotação evitam crescimento ilimitado do arquivo.
"""
import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler


def criar_logger(pasta, nome='aplicacao'):
    pasta.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f'elas.{nome}.{pasta.resolve()}')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = RotatingFileHandler(pasta / f'{nome}.log', maxBytes=1_000_000,
                                      backupCount=3, encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
    return logger


def registrar(logger, acao, resultado, registro_id=None):
    # Os valores de ação e resultado são definidos no programa, não pelo visitante.
    logger.info(json.dumps({
        'data_hora': datetime.now(timezone.utc).isoformat(),
        'acao': acao, 'resultado': resultado, 'registro_id': registro_id,
    }, ensure_ascii=False))
