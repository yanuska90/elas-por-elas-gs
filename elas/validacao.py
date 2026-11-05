"""Validação no servidor: o HTML ajuda o uso, mas não é uma barreira de segurança."""
import re
import unicodedata

TIPOS = {'doacao', 'pedido', 'permuta', 'oportunidade'}
CATEGORIAS = {'itens', 'aprendizagem', 'trabalho'}
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
    permitidos = obrigatorios | {'contrapartida'}
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
    if limpos['tipo'] == 'oportunidade' and limpos['categoria'] == 'itens':
        raise ErroValidacao('Oportunidades devem ser de aprendizagem ou trabalho.')
    if edicao:
        limpos['versao'] = inteiro(dados['versao'], 'Versão')
    return limpos


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
