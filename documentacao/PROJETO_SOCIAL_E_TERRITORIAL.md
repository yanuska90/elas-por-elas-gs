# Elas por Elas: cuidado, recursos e território

**Yanuska Monalisa Antunes Yabiku · RM 571686 · 1TDCA-2026**

## Da experiência cotidiana à proposta

A concepção da aluna integra necessidades que aparecem juntas na vida de mulheres e mães solo: alimentação, aprendizagem, deslocamento, cuidado, renda, moradia e acesso a direitos. A proposta dá continuidade ao Elas por Elas da disciplina de Linux e busca integrar todas as disciplinas da faculdade em torno de um mesmo problema social. A implementação desta GS cobre Python, Web, bancos de dados, APIs, arquivos, redes e segurança; não afirma que todos os trabalhos das outras disciplinas já estejam integrados tecnicamente.

O IBGE registrou 21,3 horas semanais de cuidado/afazeres para mulheres em 2022. Na PNAD Contínua 2024, 24,2% dos domicílios tinham algum grau de insegurança alimentar. São evidências nacionais para contextualizar a proposta. Não foram realizadas entrevistas, pesquisa municipal ou piloto com beneficiárias. Fontes completas em FONTES_E_AUTORIA.md.

## Duas partes que se complementam

**Mural social:** organiza ofertas e pedidos em quinze áreas, com tipos doação, pedido, permuta e oportunidade. Cestas, excedentes de restaurantes e marmitas podem se conectar quando estão no mesmo município, abertos e dentro do prazo. A verificação das condições e a realização do atendimento continuam humanas. Pedir ajuda não exige oferecer nada em troca.

**Diagnóstico territorial:** reúne necessidades gerais por município e setor. A coordenação acompanha registros, prioridades e situações e gera uma minuta para discussão de projetos públicos. O banco mantém separados os exemplos fictícios dos cadastros com fonte pública. Nem uma prioridade atribuída pela gestão nem uma cor no mapa provam vulnerabilidade ou risco de uma comunidade.

## Áreas e ODS: relação proposta

| Área da solução | Contribuição pretendida | ODS |
|---|---|---|
| Alimentos, marmitas e excedentes | Apoio alimentar e aproveitamento responsável; relação com acesso à alimentação e redução de desperdício | 2 e 12 |
| Educação e inclusão digital | Materiais, oficinas e compartilhamento de conhecimentos | 4 e 10 |
| Saúde, cuidado pessoal e lazer | Visibilidade de atividades e serviços, sem consulta clínica | 3, 5 e 11 |
| Preparação profissional | Capacitação e divulgação de oportunidades fictícias | 8 e 10 |
| Direitos e apoio jurídico | Divulgação de canais e atividades informativas, sem aconselhamento individual | 10 e 16 |
| Caronas e transporte | Organização de deslocamentos e diagnóstico de acesso, sem viagens reais | 10 e 11 |
| Moradia e segurança | Discussão de programas habitacionais, iluminação e convivência; sem cadastro de vítimas | 11 e 16 |
| Saneamento e óleo usado | Discussão de água/esgoto e destinação adequada de resíduos | 6, 11 e 12 |
| Recicláveis, orgânicos e hortas | Circulação de materiais, compostagem e educação ambiental | 2, 11, 12 e 13 |
| Foco em mulheres e mães solo | Considerar a sobrecarga de cuidado e barreiras de participação | 5 e 10 |

Do enunciado, estão contemplados 2, 3, 4, 10, 11 e 13. Os demais são conexões complementares. ODS 13 relaciona-se à proposta educativa e ambiental; não há cálculo de emissões evitadas. Nenhum ODS é declarado atingido por existir um botão ou cadastro.

## Modelo e procedimento para propor ampliação pública

1. Registrar uma necessidade municipal com título e descrição geral; escolher setor, prioridade e situação.
2. Se for dado público, indicar a fonte governamental que de fato sustenta o texto e a abrangência territorial. Revisar período, denominador, duplicidades e limites.
3. Consultar malha municipal do IBGE. O mapa usa limites simplificados e ponto aproximado, sem rastrear dispositivos ou residências.
4. Agrupar por município e setor. Exibir total de cadastros, pendentes e alta prioridade. Refletir que dez cadastros podem descrever o mesmo problema.
5. Baixar JSON e imprimir minuta. Complementar com escuta comunitária, orçamento, público, cronograma, órgão responsável e indicadores antes de apresentar formalmente.
6. Registrar manualmente a situação após acompanhamento. A aplicação não faz protocolo, não garante orçamento e não aprova benefícios.

O protótipo é municipal. Desagregação por bairros ou setores censitários exigiria outra base oficial, revisão de cobertura e avaliação de riscos de exposição. Não há mapa real de ocorrências criminais nem pontuação de pessoas.

## Integração entre disciplinas

| Frente | Conexão no projeto | Limite da entrega |
|---|---|---|
| Coding for Security | Funções, estruturas, arquivos JSON, Flask, requests e exceções | Implementado e testado |
| Banco de dados | Modelo relacional com cinco tabelas, chaves, transações e SQL parametrizado | MySQL real, sem ORM |
| Redes | Sockets TCP, JSON delimitado por linha, token, timeout e ACK | Comunicação local; não exposta publicamente |
| Linux e infraestrutura | Continuidade conceitual; serviços, configuração por ambiente e Compose | Modo Windows nativo validado; implantação Linux não executada nesta revisão |
| Segurança | Validação, credenciais, acesso, logs e minimização | Protótipo; não certificação de conformidade |
| Arquitetura e gestão | Separação de responsabilidades, limites, evidências e planejamento social | Viabilidade social ainda precisa de piloto |

## Validação e próximos passos

Foram executados testes técnicos, com dados fictícios e bases oficiais abertas. A validação social futura deve envolver participantes voluntárias e organizações mediadoras. Medir: tempo para encontrar apoio, compreensão dos filtros, precisão das sugestões e facilidade de registrar uma demanda. Antes de uso real, estabelecer moderação, governança, acessibilidade, responsabilidades sanitárias, segurança das caronas e procedimentos de privacidade.

A proposta adapta o tema CitizenTech. Caso a professora a classifique como ideia própria, vale a aprovação prevista no enunciado. A demonstração não substitui essa decisão nem a arguição individual.
