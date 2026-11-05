# Fontes, referências e assistência

Responsável acadêmica: Yanuska Monalisa Antunes Yabiku, RM 571686. Data de organização desta versão: 05/11/2026.

## Problema e dados públicos

1. [FIAP — CitizenTech](https://experience.fiap.com.br/global-solution-citizen-tech). Contexto da Global Solution, participação cidadã, capacitação e inclusão. O nome Elas por Elas é a proposta trazida pela aluna, em continuidade ao trabalho de Linux; não se apresenta como solução oficial da FIAP.
2. [IBGE Educa — As mulheres do Brasil](https://educa.ibge.gov.br/jovens/materias-especiais/22052-as-mulheres-do-brasil). Dado de 2022: 21,3 horas semanais de cuidados/afazeres entre mulheres. Evidência contextual, não pesquisa local nem prova de eficácia do protótipo.
3. [IBGE — API de Localidades](https://servicodados.ibge.gov.br/api/docs/localidades). Fonte de códigos e nomes de municípios. Consulta usada: [municípios de SP](https://servicodados.ibge.gov.br/api/v1/localidades/estados/SP/municipios). Snapshot real com 645 itens, em 05/11/2026. Não contém cadastro de pessoas.
4. [ONU — ODS 4](https://sdgs.un.org/goals/goal4) e [ONU — ODS 10](https://sdgs.un.org/goals/goal10). Relações propostas com aprendizagem e inclusão social/econômica. O sistema não mede os indicadores oficiais desses objetivos.

## Referências técnicas e bibliotecas

- [Flask: segurança](https://flask.palletsprojects.com/en/stable/web-security/): desenho das rotas, cabeçalhos e limites.
- [MySQL Connector/Python: execute](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html): parâmetros de consulta separados dos valores.
- [Python: sockets](https://docs.python.org/3/library/socket.html): cliente/servidor TCP.
- [Requests](https://requests.readthedocs.io/en/latest/): HTTP e interpretação JSON.
- [python-dotenv](https://github.com/theskumar/python-dotenv): leitura da configuração local.
- [Waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/): servidor WSGI para a execução local.
- Bibliotecas padrão: unittest, logging, json, pathlib, datetime, secrets, socket, socketserver, threading, uuid, hmac e zipfile.

Dependências e versões estão em `requirements.txt`. Cada biblioteca mantém sua autoria e licença própria. Não há modelo visual de terceiros, fotos de pessoas ou trechos de projetos externos copiados sem indicação. O ícone e a interface desta versão foram produzidos para o protótipo.

## Relação com aulas e projeto anterior

Foram consultados os exemplos de desenvolvimento web/REST das aulas disponibilizadas, especialmente a separação entre rotas Flask e conexão MySQL com parâmetros. A arquitetura foi adaptada para este problema. O conceito e o nome retomam o site Elas por Elas fornecido na pasta do trabalho de Linux; a interface desta GS foi reimplementada, com API, persistência e sockets próprios desta entrega. Não se afirma que a GS já esteja implantada na VM Linux.

## Declaração de IA

Houve apoio de IA generativa na estruturação, geração e revisão do código, documentação e testes. Essa participação é declarada de forma explícita também no relatório de três páginas. Não se atribui à aluna uma revisão ou domínio que ainda não tenha ocorrido.

O enunciado autoriza assistência para estudo e depuração. Como a assistência nesta preparação incluiu geração, seu alcance precisa ser apresentado à professora. A aluna deve estudar, adaptar, validar as decisões e explicar o código na arguição, respeitando as regras da avaliação individual. Não há garantia de nota ou aceitação. O guia pessoal contém perguntas e exercícios para essa preparação.

## Evidências e limites

Prints e resultados técnicos incluídos correspondem à execução local realizada. Não foram inventadas entrevistas, nomes de beneficiárias, parcerias, número de atendimentos ou resultados sociais. Os oito anúncios de exemplo são fictícios e identificados como demonstração.
