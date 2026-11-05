import json
import socket
import tempfile
import threading
import unittest
import uuid
from pathlib import Path
from receptor_tcp import criar_servidor
from elas.notificacoes import enviar_aviso


class TestTCP(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.config={'TCP_TOKEN':'segredo_ficticio_somente_para_testes_123',
                     'LOG_DIR':Path(self.temp.name),'TCP_HOST':'127.0.0.1'}
        self.servidor=criar_servidor(self.config,('127.0.0.1',0))
        self.config['TCP_PORT']=self.servidor.server_address[1]
        self.thread=threading.Thread(target=self.servidor.serve_forever,daemon=True)
        self.thread.start()
        self.aviso={'id':str(uuid.uuid4()),'anuncio_id':1,'acao':'criar'}

    def tearDown(self):
        self.servidor.shutdown(); self.servidor.server_close(); self.thread.join()
        # Fecha handlers no Windows antes de remover a pasta temporária.
        import logging
        for nome,logger in list(logging.Logger.manager.loggerDict.items()):
            if isinstance(logger,logging.Logger) and self.temp.name in nome:
                for handler in logger.handlers[:]: handler.close(); logger.removeHandler(handler)
        self.temp.cleanup()

    def test_envia_tcp_real_com_ack(self):
        self.assertTrue(enviar_aviso(self.config,self.aviso))
        texto=(Path(self.temp.name)/'tcp.log').read_text(encoding='utf-8')
        self.assertIn(self.aviso['id'],texto)
        self.assertNotIn(self.config['TCP_TOKEN'],texto)

    def test_rejeita_token_incorreto(self):
        self.assertFalse(enviar_aviso(dict(self.config,TCP_TOKEN='errado'),self.aviso))

    def test_rejeita_token_unicode_sem_quebrar_servidor(self):
        self.assertFalse(enviar_aviso(dict(self.config,TCP_TOKEN='inválido'),self.aviso))
        self.assertTrue(enviar_aviso(self.config,self.aviso))

    def test_rejeita_mensagem_acima_do_limite(self):
        with socket.create_connection(('127.0.0.1',self.config['TCP_PORT']),timeout=3) as s:
            s.sendall(b'x'*4097+b'\n'); resultado=json.loads(s.recv(4096))
        self.assertFalse(resultado['ok'])
