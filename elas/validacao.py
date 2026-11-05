"""Validação no servidor: o HTML ajuda o uso, mas não é uma barreira de segurança."""
import re
import unicodedata
from datetime import datetime, timezone
from .catalogo import CATEGORIAS_INFO, ALIMENTARES, AMBIENTAIS

TIPOS = {'doacao', 'pedido', 'permuta', 'oportunidade'}
CATEGORIAS = set(CATEGORIAS_INFO)
ESTADOS_ANUNCIO = {'aberto', 'reservado', 'concluido'}
UFS = set('AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO'.split())


class ErroValidacao(ValueError):
    """Erro esperado cuja mensagem pode ser exibida à pessoa usuária."""


def texto(valor, campo, minimo, maximo):
    if not isinstance(valor, str):
        raise ErroValidacao(f'{campo}: informe um texto.')
    valor = unicodedata.normalize('NFC', valor).strip()
    if not minimo <= len(valor) <= maximo:
        raise ErroValidacao(f'{campo}: use de {minimo} a {maximo} caracteres.')
    if any(unicodedata.category(c).startswith('C') and c not in '\n\t' for c in valor):
        raise ErroValidacao(f'{campo}: há caracteres de controle inválidos.')
    if '<' in valor or '>' in valor:
        raise ErroValidacao(f'{campo}: use texto simples, sem marcação HTML.')
    # Minimização adicional para a demonstração. Não substitui revisão humana.
    if re.search(r'\S+@\S+|https?://|www\.|(?:\d[\s()./-]*){8,}', valor, re.I):
        raise ErroValidacao(f'{campo}: não inclua contatos, documentos ou links.')
    return valor


def inteiro(valor, campo, minimo=1, maximo=2_000_000_000):
    # bool é subclasse de int em Python; True não pode representar uma quantidade.
    if type(valor) is not int or not minimo <= valor <= maximo:
        raise ErroValidacao(f'{campo}: número inteiro fora do intervalo permitido.')
    return valor


def validar_anuncio(dados, edicao=False):
    if not isinstance(dados, dict):
        raise ErroValidacao('Envie um objeto JSON.')
    obrigatorios = {'titulo', 'tipo', 'categoria', 'descricao', 'municipio_id', 'status'}
    if edicao:
        obrigatorios.add('versao')
    permitidos = obrigatorios | {'contrapartida','detalhes'}
    if not obrigatorios <= dados.keys() or dados.keys() - permitidos:
        raise ErroValidacao('Campos ausentes ou desconhecidos no anúncio.')
    for campo, escolhas in (('tipo', TIPOS), ('categoria', CATEGORIAS), ('status', ESTADOS_ANUNCIO)):
        if not isinstance(dados[campo], str) or dados[campo] not in escolhas:
            raise ErroValidacao(f'{campo}: opção não permitida.')
    limpos = {
        'titulo': texto(dados['titulo'], 'Título', 5, 100),
        'tipo': dados['tipo'], 'categoria': dados['categoria'],
        'descricao': texto(dados['descricao'], 'Descrição', 15, 800),
        'municipio_id': inteiro(dados['municipio_id'], 'Município', 1_000_000, 9_999_999),
        'status': dados['status'],
        'contrapartida': texto(dados.get('contrapartida', ''), 'Contrapartida', 0, 200),
    }
    if limpos['tipo'] == 'permuta' and len(limpos['contrapartida']) < 5:
        raise ErroValidacao('Na permuta, descreva o que gostaria de receber em troca.')
    if limpos['tipo'] != 'permuta' and limpos['contrapartida']:
        raise ErroValidacao('Doação e pedido de apoio não exigem contrapartida.')
    if limpos['tipo'] == 'permuta' and limpos['categoria'] in {'juridico','saude'}:
        raise ErroValidacao('Neste protótipo, saúde e jurídico oferecem encaminhamentos, sem permuta profissional.')
    limpos['detalhes'] = validar_detalhes(dados.get('detalhes',{}), limpos['categoria'], limpos['tipo'], limpos['status'])
    if edicao:
        limpos['versao'] = inteiro(dados['versao'], 'Versão')
    return limpos


def validar_detalhes(dados, categoria, tipo, status):
    """Esquema fechado dentro da coluna JSON; formato variável não significa livre."""
    campos={'quantidade','unidade','disponivel_ate','cuidados','origem','destino'}
    if not isinstance(dados,dict) or dados.keys()-campos:
        raise ErroValidacao('Detalhes do anúncio inválidos.')
    d={}
    if 'quantidade' in dados:
        d['quantidade']=inteiro(dados['quantidade'],'Quantidade',1,100000)
        unidades={'unidade','kg','litro','porcao','vaga','hora'}
        if not isinstance(dados.get('unidade'),str) or dados['unidade'] not in unidades:
            raise ErroValidacao('Escolha a unidade da quantidade.')
        d['unidade']=dados['unidade']
    elif 'unidade' in dados:
        raise ErroValidacao('Informe a quantidade para a unidade escolhida.')
    for k in ('cuidados','origem','destino'):
        if k in dados:
            d[k]=texto(dados[k],k,3,400 if k=='cuidados' else 80)
    if 'disponivel_ate' in dados:
        valor=dados['disponivel_ate']
        if not isinstance(valor,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',valor):
            raise ErroValidacao('Informe disponibilidade em data e hora UTC.')
        try: instante=datetime.strptime(valor,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        except ValueError: raise ErroValidacao('Data de disponibilidade inválida.')
        if status=='aberto' and instante<=datetime.now(timezone.utc):
            raise ErroValidacao('Um anúncio aberto precisa de disponibilidade futura.')
        d['disponivel_ate']=valor
    if categoria in ALIMENTARES and tipo!='pedido':
        if not {'quantidade','unidade','disponivel_ate','cuidados'}<=d.keys():
            raise ErroValidacao('Alimentos: informe quantidade, prazo e condições de conservação/ingredientes.')
        if d['unidade'] not in {'kg','porcao','unidade','litro'}:
            raise ErroValidacao('Unidade incompatível com alimentos.')
    if categoria=='caronas':
        if not {'origem','destino','disponivel_ate'}<=d.keys():
            raise ErroValidacao('Carona: informe regiões de origem/destino e data/hora.')
        if tipo!='pedido' and (d.get('unidade')!='vaga' or d.get('quantidade',0)>8):
            raise ErroValidacao('Na oferta de carona, informe de 1 a 8 vagas.')
    elif 'origem' in d or 'destino' in d:
        raise ErroValidacao('Origem e destino são usados somente em caronas.')
    if categoria in AMBIENTAIS and tipo!='pedido' and 'cuidados' not in d:
        raise ErroValidacao('Informe separação, aceitação ou condições de coleta do material.')
    return d


def validar_filtros(args):
    permitidos = {'tipo', 'categoria', 'status', 'municipio_id', 'busca', 'pagina'}
    if set(args) - permitidos or any(len(args.getlist(k)) > 1 for k in args):
        raise ErroValidacao('Filtro desconhecido ou repetido.')
    resultado = {}
    for campo, escolhas in (('tipo', TIPOS), ('categoria', CATEGORIAS), ('status', ESTADOS_ANUNCIO)):
        if args.get(campo):
            if args[campo] not in escolhas:
                raise ErroValidacao(f'Filtro {campo} inválido.')
            resultado[campo] = args[campo]
    for campo in ('municipio_id', 'pagina'):
        if args.get(campo):
            if not re.fullmatch(r'[0-9]{1,10}', args[campo]):
                raise ErroValidacao(f'Filtro {campo} inválido.')
            resultado[campo] = inteiro(int(args[campo]), campo)
    if args.get('busca'):
        resultado['busca'] = texto(args['busca'], 'Busca', 1, 80)
    return resultado
