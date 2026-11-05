"""Inicializa o esquema e atende HTTP com Waitress, sem depurador público."""
import time
import mysql.connector
from waitress import serve
from elas.configuracao import carregar_configuracao
from elas.banco import Repositorio
from elas.aplicacao import criar_app


if __name__ == '__main__':
    config = carregar_configuracao()
    repo = Repositorio(config)
    for tentativa in range(30):
        try:
            repo.inicializar()
            break
        except mysql.connector.Error:
            if tentativa == 29:
                raise SystemExit('MySQL indisponível. Confira o README e a configuração local.')
            time.sleep(2)
    print(f"Elas por Elas disponível na porta {config['APP_PORT']}.", flush=True)
    serve(criar_app(config, repo), host=config['APP_HOST'], port=config['APP_PORT'],
          threads=4, max_request_body_size=16384)
