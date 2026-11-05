"""Cria um banco separado para testes usando a senha administrativa do .env.

O servidor web nunca usa a conta root. Este comando administrativo é opcional,
destinado somente ao laboratório e não apaga nenhum banco existente.
"""
import os
import re
import mysql.connector
from elas.configuracao import carregar_configuracao


if __name__ == '__main__':
    config=carregar_configuracao()
    nome=config['DB_NAME']+'_teste'
    if not re.fullmatch(r'[a-zA-Z0-9_]{1,60}',nome):
        raise SystemExit('Nome do banco não permitido.')
    # Identificadores SQL não aceitam %s; o nome acima passa por lista restrita.
    # Senhas e nomes de contas continuam sendo passados como parâmetros.
    c=mysql.connector.connect(host=config['DB_HOST'],port=config['DB_PORT'],
                              user='root',password=os.environ['MYSQL_ROOT_PASSWORD'],connection_timeout=5)
    with c.cursor() as cur:
        cur.execute(f'CREATE DATABASE IF NOT EXISTS `{nome}` CHARACTER SET utf8mb4')
        cur.execute('SELECT Host FROM mysql.user WHERE User=%s',(config['DB_USER'],))
        hosts=[linha[0] for linha in cur.fetchall()]
        if not hosts: raise SystemExit('Usuário da aplicação não encontrado.')
        for host in hosts:
            cur.execute(f'GRANT ALL PRIVILEGES ON `{nome}`.* TO %s@%s',(config['DB_USER'],host))
    c.close()
    print('Banco exclusivo de testes preparado. O banco principal foi preservado.')
