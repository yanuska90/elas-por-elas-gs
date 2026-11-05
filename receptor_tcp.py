"""Receptor independente de avisos. Execute: python receptor_tcp.py.

Uso local de laboratório; TCP puro não fornece criptografia. No Docker o
receptor fica apenas na rede interna. Nunca publicar esta porta na internet.
Yanuska Monalisa Antunes Yabiku - RM 571686.
"""
import hmac
import json
import socketserver
import uuid
from elas.configuracao import carregar_configuracao
from elas.auditoria import criar_logger, registrar


def criar_servidor(config, endereco=None):
    logger = criar_logger(config['LOG_DIR'], 'tcp')

    class Tratador(socketserver.StreamRequestHandler):
        def handle(self):
            self.request.settimeout(2)
            try:
                linha = self.rfile.readline(4097)
                if len(linha) > 4096 or not linha.endswith(b'\n'):
                    raise ValueError()
                mensagem = json.loads(linha)
                if not isinstance(mensagem, dict) or set(mensagem) != {'id','anuncio_id','acao','token'}:
                    raise ValueError()
                token = mensagem['token']
                if not isinstance(token, str) or len(token) > 200 or not hmac.compare_digest(token.encode(), config['TCP_TOKEN'].encode()):
                    raise ValueError()
                if not isinstance(mensagem['id'], str):
                    raise ValueError()
                identificador = str(uuid.UUID(mensagem['id']))
                if identificador != mensagem['id'] or mensagem['acao'] not in ('criar','atualizar','excluir'):
                    raise ValueError()
                if type(mensagem['anuncio_id']) is not int or not 0 < mensagem['anuncio_id'] < 2_000_000_000:
                    raise ValueError()
                # O log pode repetir um UUID após reenvio: entrega é pelo menos uma vez.
                registrar(logger, 'aviso_' + mensagem['acao'], 'recebido:' + identificador,
                          mensagem['anuncio_id'])
                resposta = {'ok': True, 'id': identificador}
            except (ValueError, TypeError, KeyError, OSError):
                registrar(logger, 'tcp_receber', 'rejeitado')
                resposta = {'ok': False}
            try:
                self.wfile.write((json.dumps(resposta) + '\n').encode('utf-8'))
            except OSError:
                pass  # O cliente pode ter encerrado; o remetente repetirá o aviso.

    class Servidor(socketserver.TCPServer):
        allow_reuse_address = True

    return Servidor(endereco or (config['TCP_BIND'], config['TCP_PORT']), Tratador)


if __name__ == '__main__':
    config = carregar_configuracao()
    with criar_servidor(config) as servidor:
        print('Receptor TCP pronto. Use Ctrl+C para encerrar.', flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print('Receptor encerrado.')
