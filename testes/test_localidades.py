import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
import requests
from elas.localidades import Localidades, FonteIndisponivel
from elas.configuracao import RAIZ
from elas.validacao import ErroValidacao


class TestLocalidades(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.config = {'CACHE_DIR':Path(self.temp.name),'CACHE_TTL_HOURS':24,
                       'SNAPSHOT':RAIZ/'dados/municipios_sp.json'}
        self.fonte = Localidades(self.config)

    def tearDown(self):
        self.temp.cleanup()

    def resposta(self):
        r = Mock()
        r.__enter__ = Mock(return_value=r); r.__exit__ = Mock(return_value=False)
        r.status_code = 200
        r.iter_content.return_value = [json.dumps([{'id':3548708,'nome':'São Bernardo do Campo'}]).encode()]
        return r

    def test_api_e_cache_e_timeout_configurado(self):
        with patch('elas.localidades.requests.get',return_value=self.resposta()) as chamada:
            primeiro = self.fonte.consultar('SP')
            segundo = self.fonte.consultar('SP')
        self.assertEqual(primeiro['origem'],'api_ibge')
        self.assertEqual(segundo['origem'],'cache')
        chamada.assert_called_once()
        self.assertEqual(chamada.call_args.kwargs['timeout'],(3,8))
        self.assertFalse(chamada.call_args.kwargs['allow_redirects'])

    def test_timeout_preserva_snapshot_publico(self):
        with patch('elas.localidades.requests.get',side_effect=requests.Timeout):
            r = self.fonte.consultar('SP')
        self.assertEqual(r['origem'],'snapshot_publico')
        self.assertTrue(r['desatualizado']); self.assertEqual(len(r['items']),645)

    def test_timeout_reutiliza_cache_vencido(self):
        with patch('elas.localidades.requests.get',return_value=self.resposta()): self.fonte.consultar('SP')
        arquivo = self.config['CACHE_DIR']/'municipios_SP.json'
        os.utime(arquivo,(time.time()-90000,time.time()-90000))
        with patch('elas.localidades.requests.get',side_effect=requests.Timeout): r=self.fonte.consultar('SP')
        self.assertEqual(r['origem'],'cache'); self.assertTrue(r['desatualizado'])

    def test_uf_sem_cache_retorna_indisponibilidade(self):
        with patch('elas.localidades.requests.get',side_effect=requests.ConnectionError):
            with self.assertRaises(FonteIndisponivel): self.fonte.consultar('RJ')

    def test_nao_aceita_url_ou_caminho_como_uf(self):
        with self.assertRaises(ErroValidacao): self.fonte.consultar('../../segredo')

    def test_resposta_invalida_nao_sobrescreve_dados(self):
        r=self.resposta(); r.iter_content.return_value=[b'nao e json']
        with patch('elas.localidades.requests.get',return_value=r): resultado=self.fonte.consultar('SP')
        self.assertEqual(resultado['origem'],'snapshot_publico')
        self.assertFalse((self.config['CACHE_DIR']/'municipios_SP.json').exists())
