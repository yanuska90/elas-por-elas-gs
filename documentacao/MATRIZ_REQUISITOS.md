# Matriz do enunciado

Yanuska Monalisa Antunes Yabiku · RM 571686

| Exigência | Implementação | Evidência / verificação |
|---|---|---|
| Problema e cidadã | Mural de apoio a mulheres e mães solo; hipótese de reduzir dispersão de ofertas | README, relatório; dado público IBGE; sem entrevista inventada |
| CitizenTech e ODS | Participação comunitária, aprendizagem e inclusão; ODS 4 e 10 | Relatório, fontes; recorte próprio sujeito à regra de aprovação da professora |
| GET, POST, PUT, DELETE | Recurso `/api/anuncios`, Flask | `elas/aplicacao.py`; `validacao_http.json`; prints 03 a 06 |
| Status HTTP corretos | 200, 201 com Location, 204; erros 400/401/403/404/405/409/413/415/429/503 | Testes de integração e ciclo HTTP real |
| MySQL ou MongoDB sem ORM | MySQL Connector/Python; CRUD direto; três tabelas | `elas/banco.py`, `sql/esquema.sql`; testes em MySQL 8.4.13 real |
| Fonte externa requests + JSON | API de municípios IBGE, cache e snapshot | `elas/localidades.py`; prints 07/08; `consulta_ibge.json` |
| Interface HTML/CSS consumindo API | Mural, filtros, formulário e gestão; fetch em JavaScript | `visao/index.html`, `static`; nove prints reais |
| Log em arquivo | JSON por linha, UTC, ação e resultado, rotação | `elas/auditoria.py`; amostras JSONL em `evidencias` |
| Módulo de redes ou LLM | Cliente e receptor sockets TCP com ACK e token | `elas/notificacoes.py`, `receptor_tcp.py`; quatro testes TCP e logs reais |
| Funções, módulos e exceções | Separação de API, banco, validação, dados externos, auditoria e avisos | Pasta `elas`; testes unitários e integração |
| Execução do zero | Passos Windows Docker e modo nativo, configuração e exemplos | README, `preparar.py`, `compose.yaml`, `requirements.txt` |
| Credenciais em .env | Geração local de segredos; exemplo sem valores reais | `preparar.py`, `.env.example`, exclusões do empacotador |
| SQL parametrizado | Parâmetros separados em consultas e mutações | `elas/banco.py`; preparação administrativa valida identificadores |
| Validação de entradas | Esquemas fechados, tipos, intervalos, conteúdo, IDs, filtros e UF | `elas/validacao.py`, `elas/localidades.py`, testes |
| Erros sem detalhes internos | Respostas JSON genéricas e códigos apropriados | `elas/aplicacao.py`; testes de falhas |
| Minimização e três ameaças | Sem cadastro pessoal; dados fictícios/abertos; matriz de ameaças | `SEGURANCA.md`, página 3 do relatório |
| PDF até três páginas | Problema, cidadão, ODS, arquitetura, modelo, segurança, validação e limites | `Relatorio_GS_Elas_por_Elas.pdf` |
| ZIP/RAR e GitHub | ZIP sem segredos e repositório indicado no README | Conferir endereço efetivamente publicado e arquivo final |
| IA declarada e fontes | Declaração explícita de geração/revisão, bibliotecas e referências | Relatório e `FONTES_E_AUTORIA.md` |

## O que foi realmente executado

Em 05/11/2026: 33 testes com zero falhas, zero erros e zero ignorados; MySQL Community 8.4.13 e sockets locais reais; ciclo HTTP completo; consulta real ao IBGE; cadastro, edição, conexão e exclusão pela interface; verificação visual em computador e largura móvel de 390 px. Os testes de falha de serviços externos usam simulação controlada, identificada nos testes.

## Limites e itens que dependem da aluna

O Compose foi escrito, mas a execução por Docker foi impedida pelo acesso ao mecanismo local; a validação usou MySQL nativo. Não houve piloto com cidadãs, medição de impacto, auditoria independente nem teste de carga. A arguição depende da compreensão da aluna. O alcance da assistência de IA e a classificação da ideia devem ser discutidos conforme as regras da professora. Nenhum documento garante nota ou aceitação.
