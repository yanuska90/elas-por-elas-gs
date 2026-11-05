"""Cliente TCP com confirmação: o ACK deve repetir o UUID enviado.

TCP transporta bytes em fluxo, sem preservar limites de mensagens. Por isso o
protocolo usa um JSON por linha, limite de 4096 bytes e timeout de 2 segundos.
"""
import json
import socket
from .auditoria import registrar


def enviar_aviso(config, aviso):
    mensagem = dict(aviso, token=config['TCP_TOKEN'])
    dados = (json.dumps(mensagem, ensure_ascii=False) + '\n').encode('utf-8')
    try:
        with socket.create_connection((config['TCP_HOST'], config['TCP_PORT']), timeout=2) as s:
            s.settimeout(2)
            s.sendall(dados)
            resposta = bytearray()
            while b'\n' not in resposta:
                bloco = s.recv(1024)
                if not bloco or len(resposta) + len(bloco) > 4096:
                    return False
                resposta.extend(bloco)
            ack = json.loads(resposta.split(b'\n', 1)[0])
            return ack == {'ok': True, 'id': aviso['id']}
    except (OSError, ValueError):
        return False


def despachar(config, repositorio, logger, aviso_id=None):
    entregues, pendentes = 0, 0
    for aviso in repositorio.pendentes(aviso_id):
        sucesso = enviar_aviso(config, aviso)
        repositorio.marcar_tentativa(aviso['id'], sucesso)
        registrar(logger, 'tcp_enviar', 'confirmado' if sucesso else 'pendente', aviso['anuncio_id'])
        entregues += int(sucesso)
        pendentes += int(not sucesso)
    return {'entregues': entregues, 'pendentes_no_lote': pendentes}
