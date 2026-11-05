# Matriz do enunciado

Yanuska Monalisa Antunes Yabiku · RM 571686

| Exigência | Implementação | Evidência / verificação |
|---|---|---|
| Problema e cidadã | Mural de apoio a mulheres e mães solo; hipótese de reduzir dispersão de ofertas | README, relatório; dado público IBGE; sem entrevista inventada |
| CitizenTech e ODS | Participação comunitária, aprendizagem e inclusão; ODS 2, 3, 4, 10, 11, 13; complementares 5, 6, 8, 12, 16 | Relatório, fontes; recorte próprio sujeito à regra de aprovação da professora |
| GET, POST, PUT, DELETE | Recurso `/api/anuncios`, Flask | `elas/aplicacao.py`; `validacao_http.json`; prints 03 a 06 |
| Status HTTP corretos | 200, 201 com Location, 204; erros 400/401/403/404/405/409/413/415/429/503 | Testes de integração e ciclo HTTP real |
| MySQL ou MongoDB sem ORM | MySQL Connector/Python; CRUD direto; cinco tabelas | `elas/banco.py`, `sql/esquema.sql`; testes em MySQL 8.4.13 real |
| Fonte externa requests + JSON | API de municípios IBGE, cache e snapshot | `elas/localidades.py`; prints 07/08; `consulta_ibge.json` |
| Interface HTML/CSS consumindo API | Mural, filtros, formulário e gestão; fetch em JavaScript | `visao/index.html`, `static`; prints reais da interface |
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
| IA declarada e fontes | Autoria conceitual da aluna e declaração curta de apoio técnico, bibliotecas e referências | Relatório e `FONTES_E_AUTORIA.md` |

## O que foi realmente executado

Em 05/11/2026: 47 testes com zero falhas, zero erros e zero ignorados; MySQL Community 8.4.13 e sockets locais reais; ciclo HTTP completo; consulta real ao IBGE; cadastro, edição, conexão e exclusão pela interface; verificação visual em computador e em larguras móveis. Os testes de falha de serviços externos usam simulação controlada, identificada nos testes.

## Limites e itens que dependem da aluna

O Compose foi escrito, mas a execução por Docker foi impedida pelo acesso ao mecanismo local; a validação usou MySQL nativo. Não houve piloto com cidadãs, medição de impacto, auditoria independente nem teste de carga. A arguição depende da compreensão da aluna. A classificação da ideia segue a regra de aprovação da professora. Nenhum documento garante nota ou aceitação.


## Expansão solicitada pela aluna

| Item | Onde conferir |
|---|---|
| Identificação em destaque | Topo do site: nome completo, RM, turma, projeto e disciplina |
| 15 áreas sociais e ambientais | `elas/catalogo.py`, atalhos e filtros; 25 anúncios fictícios |
| Alimentos, restaurantes e marmitas | Quantidade, prazo e condições; conexão entre três categorias |
| Caronas, permutas, pedidos e doações | Tipos de anúncio; trajetos gerais, vagas e datas; sem contrapartida nos pedidos |
| Óleo, recicláveis, orgânicos e compostagem | Regras de aceitação/coleta; exemplos de economia circular |
| Necessidades de serviços públicos | CRUD de `necessidades`, dez setores e prioridade de 1 a 3 |
| Geolocalização de regiões | `regioes` e API IBGE; três malhas reais; sem GPS de pessoas |
| Subsídio a projetos públicos | Diagnóstico por município/setor, JSON e minuta para impressão |
| Integridade das evidências | Simulação separada de cadastro com fonte pública; sem impacto inventado |
| Integração entre disciplinas | Documento social: Coding, Linux, redes, dados e segurança; distingue implementado e proposto |

A autorização para classificar a proposta como ideia própria, a arguição e eventual validação com a comunidade não são substituídas por testes de software. O PDF tem três páginas e inclui os três cenários de ameaça solicitados.
