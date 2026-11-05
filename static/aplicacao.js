/* Elas por Elas - Yanuska Monalisa Antunes Yabiku, RM 571686.
   fetch liga a interface à API. O banco, e não localStorage, guarda anúncios.
   Todo texto vindo da API entra por textContent, nunca por innerHTML. */
'use strict';
const $ = id => document.getElementById(id);
const nomesTipo = {doacao:'Doação', pedido:'Pedido de apoio', permuta:'Permuta', oportunidade:'Oportunidade'};
const nomesCategoria = {itens:'Itens essenciais', aprendizagem:'Aprendizagem', trabalho:'Trabalho'};
const nomesStatus = {aberto:'Aberto', reservado:'Reservado', concluido:'Concluído'};
let chaveGestao = ''; // Memória da página; não vai para URL, cookie ou armazenamento.
let paginaAtual = 1;
let filtrosAtuais = new URLSearchParams();
let anuncioSelecionado = null;
let idEdicao = null;
let versaoEdicao = null;
let ultimaConsulta = null;
let sequenciaCarga = 0; // Impede uma resposta antiga de substituir busca mais nova.

function criar(tag, classe, texto) {
  const el = document.createElement(tag);
  if (classe) el.className = classe;
  if (texto !== undefined) el.textContent = texto;
  return el;
}

async function api(caminho, opcoes = {}) {
  const controle = new AbortController();
  const limite = setTimeout(() => controle.abort(), 55000);
  try {
    const headers = {Accept:'application/json', ...(opcoes.headers || {})};
    if (chaveGestao) headers['X-API-Key'] = chaveGestao;
    const resposta = await fetch(caminho, {...opcoes, headers, signal:controle.signal});
    const dados = resposta.status === 204 ? null : await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || 'Não foi possível concluir a solicitação.');
    return dados;
  } catch (erro) {
    if (erro.name === 'AbortError') throw new Error('A solicitação demorou. Atualize o mural antes de repetir um cadastro.');
    if (erro instanceof TypeError) throw new Error('Não foi possível conectar. Confira se o servidor está ligado.');
    throw erro;
  } finally { clearTimeout(limite); }
}

function mensagem(texto, falha = false) {
  $('mensagem').textContent = texto;
  $('mensagem').classList.toggle('falha', falha);
  $('mensagem').hidden = false;
}

function card(item) {
  const article = criar('article','card ' + item.categoria);
  const topo = criar('div','card-topo');
  const simbolo = criar('span','icone-card',{itens:'↗',aprendizagem:'Aa',trabalho:'✦'}[item.categoria]);
  simbolo.setAttribute('aria-hidden','true');
  topo.append(simbolo, criar('span','tipo-pill',nomesTipo[item.tipo]));
  const corpo = criar('div','card-corpo');
  corpo.append(criar('p','micro',nomesCategoria[item.categoria]), criar('h3','',item.titulo),
    criar('p','descricao',item.descricao.length > 145 ? item.descricao.slice(0,145) + '…' : item.descricao),
    criar('p','local',item.municipio + ' · ' + item.uf));
  const fim = criar('div','card-final');
  const botao = criar('button','texto-botao','Ver anúncio →');
  botao.setAttribute('aria-label','Ver anúncio: ' + item.titulo);
  botao.addEventListener('click',() => detalhes(item.id));
  fim.append(criar('span','status ' + item.status,nomesStatus[item.status]),botao);
  corpo.append(fim); article.append(topo,corpo); return article;
}

async function carregarMural() {
  const sequencia = ++sequenciaCarga;
  const params = new URLSearchParams(filtrosAtuais); params.set('pagina',paginaAtual);
  $('lista-anuncios').setAttribute('aria-busy','true');
  try {
    const [dados,resumo] = await Promise.all([api('/api/anuncios?' + params),api('/api/resumo')]);
    if (sequencia !== sequenciaCarga) return;
    $('lista-anuncios').replaceChildren(...dados.items.map(card));
    $('vazio').hidden = dados.items.length !== 0;
    $('quantidade').textContent = `${dados.total} anúncio(s) encontrado(s) · registros fictícios`;
    $('pagina').textContent = `Página ${paginaAtual} de ${Math.max(1,Math.ceil(dados.total/dados.por_pagina))}`;
    $('anterior').disabled = paginaAtual <= 1;
    $('proxima').disabled = paginaAtual * dados.por_pagina >= dados.total;
    $('total-anuncios').textContent = resumo.total;
    $('total-pedidos').textContent = resumo.pedidos;
    $('total-concluidos').textContent = resumo.concluidos;
  } catch (erro) { mensagem(erro.message,true); }
  finally { if (sequencia === sequenciaCarga) $('lista-anuncios').setAttribute('aria-busy','false'); }
}

async function carregarMunicipios() {
  const dados = await api('/api/municipios');
  for (const id of ['municipio','filtro-municipio']) {
    const select = $(id); const anterior = select.value;
    select.replaceChildren(new Option(id === 'municipio' ? 'Selecione' : 'Todos os municípios',''));
    for (const item of dados.items) select.add(new Option(`${item.nome} / ${item.uf}`,String(item.id)));
    if ([...select.options].some(opcao => opcao.value === anterior)) select.value = anterior;
  }
}

function abrirFormulario(item = null) {
  if (!chaveGestao) { $('dialog-gestao').showModal(); return; }
  $('form-anuncio').reset(); $('erro-anuncio').textContent = '';
  idEdicao = item ? item.id : null; versaoEdicao = item ? item.versao : null;
  $('titulo-form').textContent = item ? 'Editar anúncio' : 'Criar anúncio';
  if (item) {
    for (const nome of ['titulo','tipo','categoria','descricao','contrapartida']) $(nome).value = item[nome];
    $('municipio').value = String(item.municipio_id); $('situacao').value = item.status;
  }
  ajustarPermuta(); $('dialog-anuncio').showModal();
}

function ajustarPermuta() {
  const permuta = $('tipo').value === 'permuta';
  $('campo-contrapartida').hidden = !permuta;
  $('contrapartida').required = permuta;
  $('contrapartida').minLength = permuta ? 5 : 0;
  if (!permuta) $('contrapartida').value = '';
}

async function detalhes(id) {
  try {
    const dados = await api('/api/anuncios/' + id); const item = dados.item;
    anuncioSelecionado = item;
    $('tipo-detalhe').textContent = nomesTipo[item.tipo] + ' · ' + nomesCategoria[item.categoria];
    $('titulo-detalhe').textContent = item.titulo;
    $('descricao-detalhe').textContent = item.descricao;
    const fatos = [['Município',item.municipio + ' / ' + item.uf],['Situação',nomesStatus[item.status]],
      ['Identificador',String(item.id)],['Atualizado',new Date(item.atualizado_em).toLocaleString('pt-BR')]];
    if (item.contrapartida) fatos.push(['Permuta voluntária',item.contrapartida]);
    $('fatos-detalhe').replaceChildren(...fatos.map(([nome,valor]) => {
      const div = criar('div'); div.append(criar('dt','',nome),criar('dd','',valor)); return div;
    }));
    $('acoes-detalhe').hidden = !chaveGestao;
    $('criterio-conexoes').textContent = 'Buscando sugestões…'; $('conexoes').replaceChildren();
    if (!$('dialog-detalhes').open) $('dialog-detalhes').showModal();
    const sugestoes = await api('/api/conexoes/' + id);
    // Se a pessoa abriu outro anúncio enquanto aguardava, ignoramos a resposta anterior.
    if (anuncioSelecionado.id !== id) return;
    $('criterio-conexoes').textContent = sugestoes.criterio;
    if (!sugestoes.items.length) $('conexoes').append(criar('li','','Nenhuma conexão disponível neste momento.'));
    for (const outro of sugestoes.items) {
      const li = criar('li'); const b = criar('button','texto-botao',outro.titulo);
      b.addEventListener('click',() => detalhes(outro.id)); li.append(b); $('conexoes').append(li);
    }
  } catch (erro) { mensagem(erro.message,true); }
}

$('filtros').addEventListener('submit',evento => {
  evento.preventDefault(); paginaAtual = 1; filtrosAtuais = new URLSearchParams();
  for (const [chave,valor] of new FormData(evento.target)) if (valor.trim()) filtrosAtuais.set(chave,valor.trim());
  $('mensagem').hidden = true; carregarMural();
});
$('limpar-filtros').addEventListener('click',() => { $('filtros').reset(); filtrosAtuais = new URLSearchParams(); paginaAtual = 1; carregarMural(); });
$('anterior').addEventListener('click',() => { paginaAtual--; carregarMural(); });
$('proxima').addEventListener('click',() => { paginaAtual++; carregarMural(); });
$('recarregar').addEventListener('click',carregarMural);
$('novo-anuncio').addEventListener('click',() => abrirFormulario());
$('abrir-gestao').addEventListener('click',() => $('dialog-gestao').showModal());
$('tipo').addEventListener('change',ajustarPermuta);
document.querySelectorAll('[data-fechar]').forEach(b => b.addEventListener('click',() => $(b.dataset.fechar).close()));

$('form-gestao').addEventListener('submit',async evento => {
  evento.preventDefault(); $('erro-gestao').textContent = '';
  chaveGestao = $('chave').value; $('chave').value = '';
  try {
    await api('/api/gestao/verificar',{method:'POST'});
    $('dialog-gestao').close(); $('painel-gestao').hidden = false;
    $('abrir-gestao').textContent = 'Gestão liberada';
    mensagem('Gestão liberada. Você pode criar, editar e excluir anúncios fictícios.');
  } catch (erro) { chaveGestao = ''; $('erro-gestao').textContent = erro.message; }
});
$('sair-gestao').addEventListener('click',() => {
  chaveGestao = ''; $('painel-gestao').hidden = true; $('acoes-detalhe').hidden = true;
  $('abrir-gestao').textContent = 'Acesso à gestão'; mensagem('Acesso de gestão encerrado.');
});

$('form-anuncio').addEventListener('submit',async evento => {
  evento.preventDefault(); $('salvar').disabled = true; $('erro-anuncio').textContent = '';
  const dados = Object.fromEntries(new FormData(evento.target));
  dados.municipio_id = Number(dados.municipio_id);
  if (idEdicao) dados.versao = versaoEdicao;
  try {
    const resposta = await api('/api/anuncios' + (idEdicao ? '/' + idEdicao : ''),{
      method:idEdicao ? 'PUT' : 'POST', headers:{'Content-Type':'application/json'},body:JSON.stringify(dados)});
    $('dialog-anuncio').close(); paginaAtual = 1;
    const pendente = resposta.notificacao.pendentes_no_lote > 0;
    mensagem('Anúncio salvo no mural.' + (pendente ? ' O aviso à rede está pendente para reenvio.' : ' Aviso à rede confirmado.'));
    await carregarMural();
  } catch (erro) { $('erro-anuncio').textContent = erro.message; }
  finally { $('salvar').disabled = false; }
});
$('editar').addEventListener('click',() => { $('dialog-detalhes').close(); abrirFormulario(anuncioSelecionado); });
$('excluir').addEventListener('click',() => { $('erro-excluir').textContent = ''; $('dialog-excluir').showModal(); });
$('confirmar-exclusao').addEventListener('click',async () => {
  $('confirmar-exclusao').disabled = true;
  try {
    await api('/api/anuncios/' + anuncioSelecionado.id,{method:'DELETE'});
    $('dialog-excluir').close(); $('dialog-detalhes').close(); paginaAtual = 1;
    mensagem('Anúncio excluído.'); await carregarMural();
  } catch (erro) { $('erro-excluir').textContent = erro.message; }
  finally { $('confirmar-exclusao').disabled = false; }
});

const estados = {AC:'Acre',AL:'Alagoas',AP:'Amapá',AM:'Amazonas',BA:'Bahia',CE:'Ceará',DF:'Distrito Federal',ES:'Espírito Santo',GO:'Goiás',MA:'Maranhão',MT:'Mato Grosso',MS:'Mato Grosso do Sul',MG:'Minas Gerais',PA:'Pará',PB:'Paraíba',PR:'Paraná',PE:'Pernambuco',PI:'Piauí',RJ:'Rio de Janeiro',RN:'Rio Grande do Norte',RS:'Rio Grande do Sul',RO:'Rondônia',RR:'Roraima',SC:'Santa Catarina',SP:'São Paulo',SE:'Sergipe',TO:'Tocantins'};
$('uf').replaceChildren(...Object.entries(estados).map(([sigla,nome]) => new Option(nome,sigla,false,sigla === 'SP')));
$('atualizar-localidades').addEventListener('click',async () => {
  $('atualizar-localidades').disabled = true; $('resultado-localidades').textContent = 'Consultando municípios…';
  try {
    ultimaConsulta = await api('/api/localidades?uf=' + encodeURIComponent($('uf').value));
    await carregarMunicipios();
    const origem = {api_ibge:'consulta ao IBGE',cache:'cache local',snapshot_publico:'arquivo público incluído no projeto'}[ultimaConsulta.origem];
    $('resultado-localidades').textContent = `${ultimaConsulta.items.length} municípios · ${origem} · consulta de ${new Date(ultimaConsulta.consultado_em).toLocaleString('pt-BR')}.` + (ultimaConsulta.desatualizado ? ' Fonte indisponível agora; usando dados anteriores.' : '');
    $('baixar-localidades').disabled = false;
  } catch (erro) { $('resultado-localidades').textContent = erro.message; }
  finally { $('atualizar-localidades').disabled = false; }
});
$('baixar-localidades').addEventListener('click',() => {
  if (!ultimaConsulta) return;
  const url = URL.createObjectURL(new Blob([JSON.stringify(ultimaConsulta,null,2)],{type:'application/json'}));
  const a = criar('a'); a.href = url; a.download = 'municipios_' + ultimaConsulta.uf + '.json';
  document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url),1000);
});
$('reenviar-avisos').addEventListener('click',async () => {
  $('reenviar-avisos').disabled = true; $('resultado-avisos').textContent = 'Reenviando avisos…';
  try {
    const dados = await api('/api/notificacoes/reenviar',{method:'POST'});
    $('resultado-avisos').textContent = `${dados.entregues} aviso(s) confirmado(s); ${dados.pendentes_no_lote} pendente(s) neste lote de até vinte.`;
  } catch (erro) { $('resultado-avisos').textContent = erro.message; }
  finally { $('reenviar-avisos').disabled = false; }
});

carregarMunicipios().catch(erro => mensagem(erro.message,true));
carregarMural();
