# Roteiro de demonstração e prints

Mantenha Docker ou os servidores nativos abertos durante a demonstração. Use dados fictícios. Pressione `Windows + Shift + S` para capturar a área desejada e salve em `evidencias`. Os arquivos 01 a 09 já incluídos foram capturados durante uma execução real; você pode substituí-los por seus próprios prints após repetir os passos.

| Momento | Ação | O que o print deve mostrar |
|---|---|---|
| 1. Página inicial | Abra `http://127.0.0.1:5055` e atualize o mural | Nome do projeto e cartões de exemplos; `01_pagina_inicial.jpg` |
| 2. Controle de acesso | Em Acesso à gestão, abra o formulário de acesso protegido | Formulário de gestão, sem qualquer chave verdadeira; `02_acesso_protegido.jpg` |
| 3. Cadastro | Libere a gestão com a chave local e preencha um anúncio fictício | Formulário; `03_formulario_cadastro.jpg` |
| 4. Persistência e conexão | Salve uma doação de itens em São Bernardo do Campo, onde existe pedido de exemplo | Anúncio criado e sugestão por município/categoria; `04_cadastro_e_conexoes.jpg` |
| 5. Atualização | Edite o anúncio criado, selecione concluído e salve | Situação alterada no mural; `05_anuncio_atualizado.jpg` |
| 6. Exclusão | Exclua somente o anúncio descartável que você criou e confirme | Mensagem de exclusão e mural sem o item; `06_exclusao_confirmada.jpg` |
| 7. Fonte externa | Na seção de localidades, consulte SP | Quantidade, origem e retorno do IBGE; `07_consulta_ibge.jpg` |
| 8. Cache | Repita uma vez a consulta | Origem cache, sem nova consulta necessária; `08_cache_local.jpg` |
| 9. Responsividade | Reduza a largura da janela ou use modo móvel do navegador | Cartões e controles legíveis; `09_tela_celular.jpg` |
| 10. Testes e logs | Rode os comandos do README e abra amostras sem segredos | Resultado dos testes e linhas com horário/ação/resultado |

Exemplo para cadastro: título “Livros para a roda de leitura”; tipo Doação; área Itens; município São Bernardo do Campo; descrição “Exemplo fictício de livros disponíveis para uma atividade comunitária.”; situação Aberto. Não inclua telefone, e-mail, CPF ou nome de pessoa atendida.

## Arquivos gerados

`evidencias/consulta_ibge.json` contém uma resposta real. `dados/municipios_sp.json` é o snapshot público usado na contingência. `resultado_testes.json` registra o teste automatizado, e `validacao_http.json` registra os status do ciclo HTTP real. As amostras de logs são JSON por linha, não um único objeto JSON.

## Demonstração de falha do TCP

No Docker, pare apenas o receptor com `docker compose stop receptor`, crie um exemplo fictício e observe a pendência do aviso. O anúncio deve permanecer no mural. Reinicie com `docker compose start receptor` e use o botão de reenvio. No modo nativo, encerre e reinicie apenas o terminal do receptor. Esse roteiro pode produzir prints adicionais; os testes já incluídos verificam a preservação do anúncio quando o envio falha.

Não pare MySQL durante edição de dados e não apague volumes. Não publique prints do `.env`. Após acrescentar suas evidências, execute `python empacotar.py` para gerar um novo ZIP e confira o conteúdo.


## Prints da ampliação

10. Abra **Áreas de apoio**: mostre as quinze frentes sociais e ambientais.
11. Abra **Mapa de necessidades**: mantenha Demonstração fictícia e mostre as malhas e a indicação de simulação.
12. Libere a gestão e cadastre uma demanda fictícia descartável: município, setor, prioridade e descrição geral. Capture antes de salvar.
13. Edite somente esse exemplo e mude para Em análise. Capture a situação atualizada; depois exclua o exemplo descartável.
14. Escolha **Registros com fonte pública** e atualize. A base vazia comprova que os dez exemplos não foram apresentados como evidência pública.
15. Escolha uma categoria de alimentos e abra os detalhes: capture quantidade, prazo e condições.
16. No mapa, baixe o JSON e use **Imprimir minuta / PDF**. Confira a minuta exibida e o aviso de simulação; faça o print. Para guardar uma cópia, clique **Imprimir esta minuta** e escolha **Salvar como PDF**. Não envie a minuta fictícia ao poder público.

O arquivo `evidencias/diagnostico_territorial.json` guarda um recorte real de execução com dados fictícios identificados. `validacao_territorial_http.json` guarda um ciclo de criar/consultar/editar/excluir executado por HTTP. Print não substitui o arquivo JSON nem comprova impacto social.
