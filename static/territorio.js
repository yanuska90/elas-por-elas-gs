/* Diagnóstico municipal: visualização dos registros, não uma estimativa populacional.
   Yanuska Monalisa Antunes Yabiku • RM 571686. Reutiliza api() e textContent.
   O desenho SVG usa malhas públicas do IBGE, sem rastrear a localização da pessoa. */
'use strict';
let diagnosticoAtual=null, necessidadeEdicao=null, necessidadeExclusao=null, cargaTerritorio=0;
const setoresNome=Object.fromEntries([...$('necessidade-setor').options].map(o=>[o.value,o.textContent]));
const estadosNecessidade={registrada:'Registrada',em_analise:'Em análise',encaminhada:'Encaminhada',concluida:'Concluída'};
function parametrosTerritorio() {
  const p=new URLSearchParams();
  for(const [k,v] of new FormData($('filtros-territorio'))) if(v) p.set(k,v);
  return p;
}
function precisaGestao() {if(chaveGestao) return false; $('dialog-gestao').showModal(); return true;}

async function carregarTerritorio() {
  const seq=++cargaTerritorio, p=parametrosTerritorio();
  diagnosticoAtual=null; $('minuta-publica').hidden=true;
  $('exportar-diagnostico').disabled=true; $('imprimir-diagnostico').disabled=true;
  $('resumo-territorio').textContent='Carregando diagnóstico…';
  try {
    const [lista,relatorio,geo]=await Promise.all([api('/api/necessidades?'+p),api('/api/diagnostico?'+p),api('/api/regioes')]);
    if(seq!==cargaTerritorio) return;
    diagnosticoAtual=relatorio;
    const natureza=relatorio.natureza==='simulado'?'SIMULAÇÃO — dados fictícios':'Cadastros com fonte pública — exigem revisão';
    $('resumo-territorio').textContent=`${natureza} · ${relatorio.registros_considerados} registro(s). Contagem de cadastros, não de pessoas.`+(relatorio.truncado?' Limite de 1.000 registros: refine os filtros.':'');
    $('lista-necessidades').replaceChildren(...lista.items.map(cardNecessidade));
    if(!lista.items.length) $('lista-necessidades').append(criar('p','vazio','Nenhuma necessidade neste recorte. Cadastre somente situações fictícias ou informações abertas com fonte adequada.'));
    $('grupos-territorio').replaceChildren(...relatorio.grupos.map(g=>{
      const el=criar('article','grupo-territorio');
      el.append(criar('h4','',g.municipio+' · '+setoresNome[g.setor]),criar('p','',`${g.pendentes} pendente(s) · ${g.alta_prioridade} de prioridade alta · ODS ${g.ods.join(', ')}`),criar('p','',g.proposta_inicial)); return el;
    }));
    desenharMapa(geo.items,lista.items);
    $('exportar-diagnostico').disabled=false; $('imprimir-diagnostico').disabled=false;
  } catch(e) {$('resumo-territorio').textContent=e.message;}
}
function cardNecessidade(item) {
  const el=criar('article','necessidade-card');
  el.append(criar('p','micro',setoresNome[item.setor]+' · '+item.municipio),criar('h3','',item.titulo),criar('p','',item.descricao),criar('p','',`Prioridade ${item.prioridade}/3 · ${estadosNecessidade[item.status]}`));
  if(item.fonte_url) {const a=criar('a','texto-botao','Consultar fonte pública ↗');a.href=item.fonte_url;a.target='_blank';a.rel='noopener noreferrer';el.append(a);}
  const acoes=criar('div','acoes');
  const editar=criar('button','texto-botao','Editar'); editar.onclick=()=>abrirNecessidade(item);
  const excluir=criar('button','texto-botao','Excluir'); excluir.onclick=()=>{if(precisaGestao())return;necessidadeExclusao=item.id;$('erro-excluir-necessidade').textContent='';$('dialog-excluir-necessidade').showModal();};
  acoes.append(editar,excluir);el.append(acoes);return el;
}
function abrirNecessidade(item=null) {
  if(precisaGestao())return;
  necessidadeEdicao=item; $('form-necessidade').reset(); $('erro-necessidade').textContent='';
  $('titulo-necessidade-form').textContent=item?'Editar necessidade':'Registrar necessidade';
  if(item) for(const [campo,id] of Object.entries({titulo:'necessidade-titulo',municipio_id:'municipio-necessidade',setor:'necessidade-setor',descricao:'necessidade-descricao',prioridade:'necessidade-prioridade',status:'necessidade-status',natureza:'necessidade-natureza',fonte_url:'necessidade-fonte'})) $(id).value=item[campo];
  ajustarFonte(); $('dialog-necessidade').showModal();
}
function ajustarFonte() {
  const publico=$('necessidade-natureza').value==='dado_publico';
  $('necessidade-fonte').disabled=!publico; $('necessidade-fonte').required=publico;
  if(!publico)$('necessidade-fonte').value='';
}
$('necessidade-natureza').addEventListener('change',ajustarFonte);
$('nova-necessidade').onclick=()=>abrirNecessidade();
$('filtros-territorio').onsubmit=e=>{e.preventDefault();carregarTerritorio();};
$('form-necessidade').onsubmit=async e=>{
  e.preventDefault(); $('salvar-necessidade').disabled=true; $('erro-necessidade').textContent='';
  const d=Object.fromEntries(new FormData(e.target));d.municipio_id=Number(d.municipio_id);d.prioridade=Number(d.prioridade);d.fonte_url=d.fonte_url||'';
  if(necessidadeEdicao)d.versao=necessidadeEdicao.versao;
  try {await api('/api/necessidades'+(necessidadeEdicao?'/'+necessidadeEdicao.id:''),{method:necessidadeEdicao?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
    $('dialog-necessidade').close();$('natureza-territorio').value=d.natureza;await carregarTerritorio();
  }catch(e){$('erro-necessidade').textContent=e.message;}finally{$('salvar-necessidade').disabled=false;}
};
$('confirmar-exclusao-necessidade').onclick=async()=>{
  $('confirmar-exclusao-necessidade').disabled=true;
  try{await api('/api/necessidades/'+necessidadeExclusao,{method:'DELETE'});$('dialog-excluir-necessidade').close();await carregarTerritorio();}
  catch(e){$('erro-excluir-necessidade').textContent=e.message;}finally{$('confirmar-exclusao-necessidade').disabled=false;}
};

// A escala é comum a todos os municípios carregados. Buracos dos polígonos
// são preservados com fill-rule evenodd. Não são exibidos endereços pessoais.
function desenharMapa(regioes,itens) {
  const svg=$('mapa-territorio');svg.replaceChildren();$('legenda-mapa').replaceChildren();
  if(!regioes.length) {$('legenda-mapa').append(criar('li','','Sem malhas salvas. Escolha um município e consulte sua geografia.'));return;}
  const contagem={};for(const i of itens)contagem[i.municipio_id]=(contagem[i.municipio_id]||0)+1;
  const todos=[];
  function pontos(v){if(typeof v[0]==='number'){todos.push(v);return;}v.forEach(pontos);}
  regioes.forEach(r=>r.geometria.geometries.forEach(g=>pontos(g.coordinates)));
  // Redução evita exceder o limite de argumentos em malhas maiores.
  const limites=todos.reduce((a,p)=>[Math.min(a[0],p[0]),Math.max(a[1],p[0]),Math.min(a[2],p[1]),Math.max(a[3],p[1])],[Infinity,-Infinity,Infinity,-Infinity]);
  const [xmin,xmax,ymin,ymax]=limites;
  const escala=Math.min(580/Math.max(.001,xmax-xmin),320/Math.max(.001,ymax-ymin));
  const cx=(xmin+xmax)/2,cy=(ymin+ymax)/2;
  const projetar=p=>[320+(p[0]-cx)*escala,190-(p[1]-cy)*escala];
  const ns='http://www.w3.org/2000/svg';
  for(const r of regioes){
    const n=contagem[r.municipio_id]||0;
    const grupo=document.createElementNS(ns,'g');
    for(const g of r.geometria.geometries){
      const poligonos=g.type==='Polygon'?[g.coordinates]:g.coordinates;
      for(const poli of poligonos){
        const path=document.createElementNS(ns,'path');
        path.setAttribute('d',poli.map(anel=>anel.map((p,i)=>(i?'L':'M')+projetar(p).join(',')).join(' ')+'Z').join(' '));
        path.setAttribute('fill',n?'#8661a8':'#ede7f2');path.setAttribute('stroke','#392149');path.setAttribute('stroke-width','1.5');path.setAttribute('fill-rule','evenodd');
        const title=document.createElementNS(ns,'title');title.textContent=r.municipio+': '+n+' registro(s) no recorte';path.append(title);grupo.append(path);
      }
    }
    // Os valores ficam na legenda para não sobrepor cidades muito próximas.
    svg.append(grupo);
    const li=criar('li'),b=criar('button','texto-botao',`${r.municipio}: ${n} registro(s)`);
    b.onclick=()=>{$('filtro-territorio').value=r.municipio_id;carregarTerritorio();};li.append(b);$('legenda-mapa').append(li);
  }
}
$('localizar-regiao').onclick=async()=>{
  if(precisaGestao())return;const ident=$('filtro-territorio').value;
  if(!ident){$('resultado-geografia').textContent='Selecione um município no filtro antes de consultar.';return;}
  $('localizar-regiao').disabled=true;$('resultado-geografia').textContent='Consultando malha pública…';
  try {const d=await api('/api/regioes/'+ident+'/localizar',{method:'POST'});const r=d.item||d;
    $('resultado-geografia').textContent=`Geografia: ${r.origem}. Referência consultada em ${new Date(r.consultado_em).toLocaleString('pt-BR')}.`+(r.desatualizado?' A fonte está indisponível; foi usada uma cópia anterior.':'');await carregarTerritorio();
  }catch(e){$('resultado-geografia').textContent=e.message;}finally{$('localizar-regiao').disabled=false;}
};
$('exportar-diagnostico').onclick=()=>{
  if(!diagnosticoAtual)return;const u=URL.createObjectURL(new Blob([JSON.stringify(diagnosticoAtual,null,2)],{type:'application/json'}));const a=criar('a');a.href=u;a.download='diagnostico_territorial_'+diagnosticoAtual.natureza+'.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),1000);
};
$('imprimir-diagnostico').onclick=()=>{
  if(!diagnosticoAtual)return;const d=diagnosticoAtual,el=$('minuta-publica');el.replaceChildren();
  el.append(criar('h1','','Elas por Elas — proposta territorial'),criar('p','','Yanuska Monalisa Antunes Yabiku · RM 571686 · GS Coding for Security'),criar('h2','',d.natureza==='simulado'?'SIMULAÇÃO ACADÊMICA — NÃO PROTOCOLAR':'MINUTA PARA REVISÃO — NÃO ENVIADA'),criar('p','',d.metodologia),criar('p','',`Gerada em ${new Date(d.gerado_em).toLocaleString('pt-BR')}. Registros no recorte: ${d.registros_considerados}.`));
  if(d.truncado)el.append(criar('p','','RECORTE PARCIAL: limite de 1.000 registros. Refine os filtros antes de utilizar.'));
  for(const g of d.grupos){el.append(criar('h3','',g.municipio+' / '+g.uf+' — '+setoresNome[g.setor]),criar('p','',`${g.registros} cadastro(s), ${g.pendentes} pendente(s); ${g.alta_prioridade} de prioridade alta. ODS ${g.ods.join(', ')}.`),criar('p','',g.proposta_inicial));for(const f of g.fontes)el.append(criar('p','','Fonte indicada: '+f));}
  el.append(criar('h3','','Antes de apresentar ao poder público'));const ol=criar('ol');d.proximos_passos.forEach(p=>ol.append(criar('li','',p)));el.append(ol,criar('p','',d.uso));
  const imprimir=criar('button','botao principal nao-imprimir','Imprimir esta minuta');imprimir.onclick=()=>window.print();el.append(imprimir);
  el.hidden=false;el.scrollIntoView({behavior:'smooth'});
};
carregarTerritorio();
