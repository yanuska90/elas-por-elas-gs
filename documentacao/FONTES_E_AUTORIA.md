# Fontes, referências e assistência

Responsável acadêmica: Yanuska Monalisa Antunes Yabiku, RM 571686. Data de organização desta versão: 05/11/2026.

## Problema e dados públicos

1. [FIAP — CitizenTech](https://experience.fiap.com.br/global-solution-citizen-tech). Contexto da Global Solution, participação cidadã, capacitação e inclusão. O nome Elas por Elas é a proposta trazida pela aluna, em continuidade ao trabalho de Linux; não se apresenta como solução oficial da FIAP.
2. [IBGE Educa — As mulheres do Brasil](https://educa.ibge.gov.br/jovens/materias-especiais/22052-as-mulheres-do-brasil). Dado de 2022: 21,3 horas semanais de cuidados/afazeres entre mulheres. Evidência contextual, não pesquisa local nem prova de eficácia do protótipo.
3. [IBGE — API de Localidades](https://servicodados.ibge.gov.br/api/docs/localidades). Fonte de códigos e nomes de municípios. Consulta usada: [municípios de SP](https://servicodados.ibge.gov.br/api/v1/localidades/estados/SP/municipios). Snapshot real com 645 itens, em 05/11/2026. Não contém cadastro de pessoas.
4. [ONU Brasil — Objetivos de Desenvolvimento Sustentável](https://brasil.un.org/pt-br/sdgs). A versão ampliada relaciona 11 objetivos: 2, 3, 4, 5, 6, 8, 10, 11, 12, 13 e 16. O nome de cada objetivo e a função correspondente estão no relatório e no documento social. O sistema não mede os indicadores oficiais desses objetivos.

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

## Autoria e apoio técnico

Concepção, narrativa e proposta de integração entre disciplinas: Yanuska Monalisa Antunes Yabiku. Utilizei IA como apoio à implementação, documentação e validação técnica.

## Evidências e limites

Prints e resultados técnicos incluídos correspondem à execução local realizada. Não foram inventadas entrevistas, nomes de beneficiárias, parcerias, número de atendimentos ou resultados sociais. Os 25 anúncios de exemplo são fictícios e identificados como demonstração.


## Ampliação social e territorial

- [IBGE - PNAD Contínua, segurança alimentar 2024](https://agenciadenoticias.ibge.gov.br/media/com_mediaibge/arquivos/724f23c52823528787ba0ef28b7940e3.pdf): 24,2% dos domicílios, cerca de 18,9 milhões, em algum grau de insegurança alimentar. Contexto nacional de 2024, sem inferência automática para bairros ou municípios.
- [IBGE - API de malhas v3](https://servicodados.ibge.gov.br/api/docs/malhas?versao=3): limites municipais simplificados em GeoJSON. Três consultas reais em 05/11/2026; código e data na cópia `dados/geografia_municipal.json`.
- [ONU - ODS](https://sdgs.un.org/goals): objetivos 2, 3, 4, 10, 11, 13 do enunciado e conexões 5, 6, 8, 12, 16. Mapeamento explicado no documento social; nenhuma meta é declarada cumprida.
- [Anvisa - Guia para doação segura de alimentos](https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2022/publicado-guia-para-doacao-de-alimentos-com-seguranca-sanitaria): referência para exigir informações e revisão das condições de doação. Não transforma o software em inspeção sanitária.
- [MMA - Compostagem](https://www.gov.br/mma/pt-br/assuntos/educacao-ambiental/glossario-ea/o-que-e-compostagem): fundamento da proposta de destinação de orgânicos e educação ambiental.
- [Paraná - Coleta de óleo de cozinha](https://www.conexaoambiental.pr.gov.br/Pagina/Coleta-oleo-de-cozinha): referência de destinação responsável, sem afirmar que um ponto de coleta específico participa do projeto.
