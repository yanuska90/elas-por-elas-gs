# Segurança e privacidade

Yanuska Monalisa Antunes Yabiku · RM 571686 · GS Coding for Security

## Escopo e dados

O ambiente é um laboratório local. Os anúncios são fictícios, e os municípios são dados públicos do IBGE. Não há cadastro de cidadãs, CPF, telefone, endereço residencial, renda ou histórico de violência. O texto livre deve continuar fictício: o bloqueio de padrões de contatos reduz erros comuns, mas não identifica todo dado pessoal possível.

Consulta é pública; criação, edição, exclusão e reenvio dependem de uma chave de gestão. Essa chave representa uma coordenação única e permite alterar qualquer anúncio. Não existe autenticação individual nem autorização por proprietária. Essa é uma limitação deliberada do protótipo, não uma solução pronta para publicação na internet.

## Três ameaças e suas mitigações

| Ameaça | Cenário | Mitigação implementada | Limitação |
|---|---|---|---|
| Injeção SQL e entrada malformada | Uma pessoa envia texto SQL no filtro ou altera tipos e campos do JSON | Valores separados da consulta com parâmetros `%s`; lista fechada de filtros, enumerações e campos; validação de tamanhos e identificadores | Não substitui atualização do servidor, revisão de consultas futuras ou controle de acesso ao banco |
| Alteração não autorizada e abuso de chamadas | Uma pessoa tenta criar ou apagar anúncios sem a chave, ou repete solicitações | Chave em `.env`, comparação com `hmac.compare_digest`, cabeçalho `X-API-Key`, conferência de origem e limite por minuto | Chave compartilhada não identifica pessoas; o limite em memória não protege contra ataque distribuído |
| Exposição de dados e execução de conteúdo no navegador | Contatos pessoais entram em anúncios, scripts são enviados ou segredos vão para logs/repositório | Modelo mínimo, dados fictícios/abertos, rejeição de HTML e padrões de contato; `textContent`, CSP; logs só com metadados; exclusão de `.env` do pacote | Filtro textual não garante anonimização; TCP local não é cifrado; implantação real exige HTTPS, contas e processos de governança |

## Proteções complementares

- A fonte externa tem domínio fixo, UFs permitidas, verificação TLS padrão do requests, timeout e limite de resposta. O usuário não fornece uma URL arbitrária.
- A mensagem de erro da API não expõe SQL, caminhos, credenciais ou rastreamentos internos.
- O MySQL usa uma conta limitada ao banco do projeto; a inicialização requer criação de tabelas. Em produção, separar migrações de CRUD e reduzir privilégios.
- Anúncio e aviso pendente são confirmados na mesma transação. Queda do receptor não desfaz o anúncio.
- O PUT compara a versão do registro e responde 409 quando a edição ficou antiga. Esse controle evita sobrescrever silenciosamente outra alteração.
- Os serviços nativos escutam em loopback por padrão. No Compose, somente web e MySQL têm portas locais; o receptor permanece na rede interna.

## Configuração e segredos

Execute `python preparar.py` para gerar senhas aleatórias. Mantenha `.env` local e use `.env.example` na entrega. Não reutilize as senhas de teste em produção. O `.gitignore` ajuda a evitar inclusão acidental; o empacotador também recusa o conteúdo dos segredos locais nos arquivos selecionados.

Os logs giram a cada 1 MB, com três cópias, e registram horário UTC, ação, resultado e identificadores técnicos. Não gravam os textos dos anúncios, chaves nem IPs. Os prints de evidência não devem exibir `.env` nem a chave em texto aberto.

## Relação com a LGPD

O projeto aplica minimização como decisão de arquitetura e usa somente exemplos fictícios e dados públicos. Não afirma certificação ou conformidade jurídica completa. Para uso real, seria necessário avaliar finalidade e base legal, transparência, responsabilidades, retenção, direitos das pessoas, moderação e resposta a incidentes. O protótipo não coleta casos reais nem serve como canal de emergência.

## Validação de segurança

Há testes de chave ausente/inválida, JSON inválido, campos inesperados, origem bloqueada, conflitos, limites, indisponibilidade e validação do protocolo TCP. Consulte `evidencias/resultado_testes.json` e os casos em `testes`. O conjunto é uma verificação funcional dirigida, não uma auditoria completa ou teste de invasão.


## Território e novas áreas

As necessidades são municipais, sem coordenadas de famílias. SQL parametrizado e controle de versão também protegem seu CRUD. A coluna JSON de detalhes aceita somente seis chaves previstas, com tipos, tamanhos e prazos validados. Demandas com fonte pública exigem URL HTTPS governamental; a aplicação não baixa a URL indicada, evitando que esse campo dispare requisições arbitrárias. A conferência do conteúdo da fonte é humana.

Dados de demonstração não são agregados com os de fonte pública. Duplicidades ainda podem existir; contagens e prioridades não são estatísticas populacionais. Logs não registram descrições nem a chave. Textos sobre saúde, jurídico e segurança não devem conter relatos pessoais; as verificações por padrão textual não garantem anonimização. Uma implantação real dependeria de moderação e análise jurídica e operacional específica.
