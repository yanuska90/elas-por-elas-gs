"""Executa testes e salva um relatório real, incluindo testes ignorados.

Uso: python verificar.py [--integracao]. Integração exige um banco _teste
previamente criado. Nunca configure o banco de teste como banco de produção.
"""
import argparse
import json
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--integracao',action='store_true')
    argumentos=parser.parse_args()
    if argumentos.integracao: os.environ['GS_TEST_MYSQL']='1'
    raiz=Path(__file__).resolve().parent
    os.chdir(raiz)
    suite=unittest.defaultTestLoader.discover('testes',top_level_dir='.')
    resultado=unittest.TextTestRunner(verbosity=2).run(suite)
    resumo={'executado_em':datetime.now(timezone.utc).isoformat(),
            'python':sys.version.split()[0], 'integracao_mysql':argumentos.integracao,
            'testes':resultado.testsRun, 'falhas':len(resultado.failures),
            'erros':len(resultado.errors), 'ignorados':len(resultado.skipped),
            'sucesso':resultado.wasSuccessful(),
            'detalhes_falhas':[str(t) for t,_ in resultado.failures+resultado.errors],
            'detalhes_ignorados':[{'teste':str(t),'motivo':m} for t,m in resultado.skipped]}
    pasta=raiz/'evidencias'; pasta.mkdir(exist_ok=True)
    (pasta/'resultado_testes.json').write_text(json.dumps(resumo,ensure_ascii=False,indent=2),encoding='utf-8')
    sys.exit(0 if resultado.wasSuccessful() else 1)
