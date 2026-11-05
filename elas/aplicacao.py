"""Rotas HTTP, autenticação e coordenação dos módulos do Elas por Elas."""
import hmac
import threading
import time
from collections import defaultdict, deque
from functools import wraps
from flask import Flask, jsonify, request, render_template
from werkzeug.exceptions import HTTPException
import mysql.connector
from .configuracao import carregar_configuracao, RAIZ
from .auditoria import criar_logger, registrar
from .validacao import validar_anuncio, validar_filtros, ErroValidacao, inteiro
from .banco import Repositorio, ConflitoEdicao
from .localidades import Localidades, FonteIndisponivel
from .notificacoes import despachar
from .catalogo import catalogo_publico, ALIMENTARES
from .territorio import Territorio, validar_necessidade, filtros_territorio, localizar_municipio


def criar_app(config=None, repositorio=None, fonte=None):
    app = Flask(__name__, template_folder=str(RAIZ / 'visao'),
                static_folder=str(RAIZ / 'static'))
    app.config.update(config or carregar_configuracao())
    app.json.ensure_ascii = False
    repo = repositorio or Repositorio(app.config)
    localidades = fonte or Localidades(app.config)
    logger = criar_logger(app.config['LOG_DIR'])
    territorio = Territorio(repo)
    app.extensions.update(repositorio=repo, localidades=localidades, auditoria=logger)
    acessos, lock = defaultdict(deque), threading.Lock()

    def erro(mensagem, status):
        resposta = jsonify({'erro': mensagem})
        if status == 401:
            resposta.headers['WWW-Authenticate'] = 'ApiKey realm="gestao"'
        return resposta, status

    def protegido(funcao):
        @wraps(funcao)
        def verificar(*args, **kwargs):
            chave = request.headers.get('X-API-Key', '')
            if not chave:
                return erro('Informe a chave de gestão.', 401)
            if len(chave) > 200 or not hmac.compare_digest(chave.encode(), app.config['API_KEY'].encode()):
                return erro('Acesso não autorizado.', 401)
            return funcao(*args, **kwargs)
        return verificar

    @app.before_request
    def limitar_e_validar_origem():
        if not request.path.startswith('/api/'):
            return None
        # Estado efêmero, limitado ao processo; não é proteção contra DDoS.
        agora = time.monotonic()
        with lock:
            for ip in list(acessos):
                if not acessos[ip] or agora - acessos[ip][-1] >= 60:
                    del acessos[ip]
            chave = request.remote_addr or 'local'
            fila = acessos[chave]
            while fila and agora - fila[0] >= 60:
                fila.popleft()
            if len(fila) >= app.config['RATE_LIMIT']:
                resposta, status = erro('Muitas solicitações. Aguarde um minuto.', 429)
                resposta.headers['Retry-After'] = '60'
                return resposta, status
            fila.append(agora)
        if request.method in ('POST','PUT','DELETE'):
            origem = request.headers.get('Origin')
            if origem and origem != request.host_url.rstrip('/'):
                return erro('Origem da solicitação não autorizada.', 403)

    @app.after_request
    def proteger_resposta(resposta):
        resposta.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        resposta.headers['X-Content-Type-Options'] = 'nosniff'
        resposta.headers['X-Frame-Options'] = 'DENY'
        resposta.headers['Referrer-Policy'] = 'no-referrer'
        resposta.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        if request.path.startswith('/api/'):
            resposta.headers['Cache-Control'] = 'no-store'
            # request.endpoint é um nome interno de rota; não contém busca ou corpo.
            registrar(logger, request.method + ':' + (request.endpoint or 'rota_inexistente'),
                      str(resposta.status_code))
        return resposta

    @app.errorhandler(ErroValidacao)
    def erro_validacao(exc):
        return erro(str(exc), 400)

    @app.errorhandler(ConflitoEdicao)
    def conflito(exc):
        return erro('Este anúncio mudou em outra janela. Recarregue antes de editar.', 409)

    @app.errorhandler(mysql.connector.Error)
    def erro_banco(exc):
        registrar(logger, 'banco', 'indisponivel')
        return erro('Serviço de dados indisponível. Tente novamente em instantes.', 503)

    @app.errorhandler(HTTPException)
    def erro_http(exc):
        mensagens = {400:'JSON inválido.',404:'Recurso não encontrado.',405:'Método não permitido.',
                     413:'Solicitação acima do limite.',415:'Envie Content-Type application/json.'}
        return erro(mensagens.get(exc.code, 'Solicitação não aceita.'), exc.code)

    @app.errorhandler(Exception)
    def erro_inesperado(exc):
        registrar(logger, 'aplicacao', 'erro_interno')
        return erro('Não foi possível concluir a operação.', 500)

    def ler_dados(edicao=False):
        if request.args:
            raise ErroValidacao('Esta operação não aceita parâmetros na URL.')
        dados = validar_anuncio(request.get_json(), edicao)
        if not repo.municipio_existe(dados['municipio_id']):
            raise ErroValidacao('Escolha um município disponível na lista.')
        return dados

    def tentar_aviso(aviso_id):
        # Erro de notificação não transforma um cadastro já confirmado em falha.
        try:
            return despachar(app.config, repo, logger, aviso_id)
        except mysql.connector.Error:
            registrar(logger, 'tcp_enviar', 'pendente')
            return {'entregues':0, 'pendentes_no_lote':1}

    @app.get('/')
    def inicio():
        return render_template('index.html',catalogo=catalogo_publico())

    @app.get('/api/catalogo')
    def catalogo():
        if request.args: raise ErroValidacao('Catálogo não aceita filtros.')
        return jsonify(catalogo_publico())

    @app.get('/api/anuncios')
    def listar_anuncios():
        return jsonify(repo.listar(validar_filtros(request.args)))

    @app.post('/api/anuncios')
    @protegido
    def criar_anuncio():
        dados = ler_dados()
        anuncio_id, aviso_id = repo.criar(dados)
        aviso = tentar_aviso(aviso_id)
        resposta = jsonify({'item': repo.obter(anuncio_id), 'notificacao': aviso})
        resposta.status_code = 201
        resposta.headers['Location'] = f'/api/anuncios/{anuncio_id}'
        registrar(logger, 'anuncio_criar', 'sucesso', anuncio_id)
        return resposta

    @app.get('/api/anuncios/<int:anuncio_id>')
    def obter_anuncio(anuncio_id):
        inteiro(anuncio_id, 'Identificador')
        if request.args:
            raise ErroValidacao('Esta consulta não aceita filtros.')
        item = repo.obter(anuncio_id)
        return jsonify({'item':item}) if item else erro('Anúncio não encontrado.',404)

    @app.put('/api/anuncios/<int:anuncio_id>')
    @protegido
    def atualizar_anuncio(anuncio_id):
        inteiro(anuncio_id, 'Identificador')
        dados = ler_dados(edicao=True)
        aviso_id = repo.atualizar(anuncio_id, dados)
        if not aviso_id:
            return erro('Anúncio não encontrado.',404)
        aviso = tentar_aviso(aviso_id)
        registrar(logger, 'anuncio_atualizar', 'sucesso', anuncio_id)
        return jsonify({'item':repo.obter(anuncio_id), 'notificacao':aviso})

    @app.delete('/api/anuncios/<int:anuncio_id>')
    @protegido
    def excluir_anuncio(anuncio_id):
        inteiro(anuncio_id, 'Identificador')
        if request.args or request.get_data():
            raise ErroValidacao('Exclusão não aceita filtros nem corpo.')
        aviso_id = repo.excluir(anuncio_id)
        if not aviso_id:
            return erro('Anúncio não encontrado.',404)
        tentar_aviso(aviso_id)
        registrar(logger, 'anuncio_excluir', 'sucesso', anuncio_id)
        return '', 204

    @app.get('/api/resumo')
    def resumo():
        if request.args:
            raise ErroValidacao('Esta consulta não aceita filtros.')
        return jsonify(repo.resumo())

    @app.get('/api/municipios')
    def municipios():
        if request.args:
            raise ErroValidacao('Esta consulta não aceita filtros.')
        return jsonify({'items':repo.municipios()})

    @app.get('/api/localidades')
    def fonte_externa():
        if set(request.args) - {'uf'} or len(request.args.getlist('uf')) > 1:
            raise ErroValidacao('Informe somente uma UF.')
        try:
            resultado = localidades.consultar(request.args.get('uf', 'SP'))
        except FonteIndisponivel:
            return erro('O IBGE está indisponível e não há cache desta UF.',503)
        repo.salvar_municipios(resultado['items'])
        registrar(logger, 'ibge_consultar', resultado['origem'])
        return jsonify(resultado)

    @app.get('/api/conexoes/<int:anuncio_id>')
    def conexoes(anuncio_id):
        inteiro(anuncio_id, 'Identificador')
        if request.args:
            raise ErroValidacao('Esta consulta não aceita filtros.')
        item = repo.obter(anuncio_id)
        if not item:
            return erro('Anúncio não encontrado.',404)
        # Regra transparente: mesma categoria e município, tipo complementar.
        if item['tipo'] not in ('pedido','doacao') or item['status'] != 'aberto' or item.get('expirado'):
            return jsonify({'items':[], 'criterio':'Conexões são sugeridas entre doações e pedidos abertos.'})
        filtros = {'categoria':item['categoria'], 'municipio_id':item['municipio_id'],
                   'tipo':'doacao' if item['tipo']=='pedido' else 'pedido', 'status':'aberto'}
        categorias=sorted(ALIMENTARES) if item['categoria'] in ALIMENTARES else [item['categoria']]
        itens=[]
        for categoria in categorias:
            filtros['categoria']=categoria
            itens.extend(i for i in repo.listar(filtros)['items'] if not i.get('expirado'))
        return jsonify({'items':itens[:12],
                        'criterio':'Mesma cidade; doações e pedidos abertos, com prazo vigente quando informado. Alimentos conectam cestas, excedentes e marmitas. Avalie descrição e condições; não há garantia de atendimento.'})

    @app.get('/api/necessidades')
    def listar_necessidades():
        return jsonify(territorio.listar(filtros_territorio(request.args)))

    def ler_necessidade(edicao=False):
        if request.args: raise ErroValidacao('Esta operação não aceita filtros.')
        dados=validar_necessidade(request.get_json(),edicao)
        if not repo.municipio_existe(dados['municipio_id']): raise ErroValidacao('Município não cadastrado.')
        return dados

    @app.post('/api/necessidades')
    @protegido
    def criar_necessidade():
        ident=territorio.salvar(ler_necessidade())
        registrar(logger,'necessidade_criar','sucesso',ident)
        resposta=jsonify({'item':territorio.obter(ident)})
        resposta.status_code=201; resposta.headers['Location']=f'/api/necessidades/{ident}'
        return resposta

    @app.get('/api/necessidades/<int:ident>')
    def obter_necessidade(ident):
        inteiro(ident,'Identificador')
        if request.args: raise ErroValidacao('Esta consulta não aceita filtros.')
        item=territorio.obter(ident)
        return jsonify({'item':item}) if item else erro('Necessidade não encontrada.',404)

    @app.put('/api/necessidades/<int:ident>')
    @protegido
    def editar_necessidade(ident):
        inteiro(ident,'Identificador')
        if not territorio.salvar(ler_necessidade(True),ident): return erro('Necessidade não encontrada.',404)
        registrar(logger,'necessidade_atualizar','sucesso',ident)
        return jsonify({'item':territorio.obter(ident)})

    @app.delete('/api/necessidades/<int:ident>')
    @protegido
    def excluir_necessidade(ident):
        inteiro(ident,'Identificador')
        if request.args or request.get_data(): raise ErroValidacao('Exclusão não aceita corpo ou filtros.')
        if not territorio.excluir(ident): return erro('Necessidade não encontrada.',404)
        registrar(logger,'necessidade_excluir','sucesso',ident)
        return '',204

    @app.get('/api/regioes')
    def regioes():
        if request.args: raise ErroValidacao('Esta consulta não aceita filtros.')
        return jsonify({'items':territorio.regioes(),'referencia':'Malhas IBGE; pontos aproximados dos municípios, sem localização de famílias.'})

    @app.post('/api/regioes/<int:ident>/localizar')
    @protegido
    def localizar(ident):
        inteiro(ident,'Município',1000000,9999999)
        if request.args or request.get_data(): raise ErroValidacao('Localização não aceita corpo ou filtros.')
        if not repo.municipio_existe(ident): raise ErroValidacao('Município não cadastrado.')
        try: resultado=localizar_municipio(ident,territorio)
        except FonteIndisponivel: return erro('Geografia indisponível. A necessidade permanece registrada.',503)
        registrar(logger,'regiao_localizar',resultado['origem'],ident)
        return jsonify(resultado)

    @app.get('/api/diagnostico')
    def diagnostico():
        return jsonify(territorio.relatorio(filtros_territorio(request.args)))

    @app.post('/api/gestao/verificar')
    @protegido
    def verificar_acesso():
        if request.args or request.get_data():
            raise ErroValidacao('Esta operação não recebe dados.')
        return jsonify({'autorizado':True})

    @app.post('/api/notificacoes/reenviar')
    @protegido
    def reenviar():
        if request.args or request.get_data():
            raise ErroValidacao('Esta operação não recebe dados.')
        return jsonify(despachar(app.config, repo, logger))

    @app.get('/api/saude')
    def saude():
        if request.args:
            raise ErroValidacao('Esta consulta não aceita filtros.')
        repo.resumo()
        return jsonify({'status':'ok', 'banco':'mysql', 'modo':'demonstracao'})

    return app
