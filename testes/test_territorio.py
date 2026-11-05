"""Casos de erro e fronteiras da expansão social/territorial."""
import unittest
from datetime import datetime,timedelta,timezone
from werkzeug.datastructures import MultiDict
from elas.validacao import validar_anuncio,ErroValidacao
from elas.territorio import validar_necessidade,filtros_territorio,extrair_geografia
from elas.localidades import FonteIndisponivel
from testes.test_validacao import exemplo

def necessidade(**trocas):
    d=dict(municipio_id=3548708,setor='alimentacao',titulo='Cozinha comunitária demonstrativa',descricao='Demanda fictícia para testar uma proposta de apoio alimentar.',prioridade=3,natureza='simulado',fonte_url='',status='registrada')
    d.update(trocas);return d

def alimento(**trocas):
    d=dict(quantidade=10,unidade='porcao',cuidados='Exemplo: validar conservação e ingredientes antes da entrega.',disponivel_ate=(datetime.now(timezone.utc)+timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ'))
    d.update(trocas);return d

class TestExpansao(unittest.TestCase):
    def test_alimento_exige_quantidade_prazo_e_condicoes(self):
        for campo in alimento():
            d=alimento();d.pop(campo)
            with self.subTest(campo=campo),self.assertRaises(ErroValidacao):validar_anuncio(exemplo(categoria='marmitas',detalhes=d))
        self.assertEqual(validar_anuncio(exemplo(categoria='excedentes',detalhes=alimento()))['detalhes']['quantidade'],10)
    def test_prazo_passado_e_data_invalida(self):
        for prazo in ['2020-01-01T00:00:00Z','2099-02-30T00:00:00Z','amanha']:
            with self.assertRaises(ErroValidacao):validar_anuncio(exemplo(categoria='alimentos',detalhes=alimento(disponivel_ate=prazo)))
    def test_detalhes_rejeitam_campo_livre_e_bool(self):
        for d in [dict(endereco='Residência'),dict(quantidade=True,unidade='kg'),dict(unidade='kg'),dict(cuidados='<script>')]:
            with self.assertRaises(ErroValidacao):validar_anuncio(exemplo(detalhes=d))
    def test_carona_exige_trajeto_e_vagas(self):
        d=alimento(unidade='vaga',quantidade=3,origem='Região central',destino='Região cultural')
        self.assertEqual(validar_anuncio(exemplo(categoria='caronas',detalhes=d))['detalhes']['quantidade'],3)
        for trocas in [dict(quantidade=9),dict(unidade='kg'),dict(origem='x')]:
            with self.assertRaises(ErroValidacao):validar_anuncio(exemplo(categoria='caronas',detalhes=dict(d,**trocas)))
    def test_reciclaveis_exigem_condicoes(self):
        for c in ['reciclaveis','oleo','compostagem','hortas']:
            with self.assertRaises(ErroValidacao):validar_anuncio(exemplo(categoria=c))
            self.assertTrue(validar_anuncio(exemplo(categoria=c,detalhes={'cuidados':'Confirmar separação e aceitação do material.'})))
    def test_fontes_nao_misturam_simulacao(self):
        with self.assertRaises(ErroValidacao):validar_necessidade(necessidade(fonte_url='https://ibge.gov.br/'))
        with self.assertRaises(ErroValidacao):validar_necessidade(necessidade(natureza='dado_publico'))
        self.assertEqual(validar_necessidade(necessidade(natureza='dado_publico',fonte_url='https://www.ibge.gov.br/'))['natureza'],'dado_publico')
    def test_fonte_rejeita_porta_invalida_e_dominio_enganoso(self):
        for fonte in ['https://www.ibge.gov.br:errada/','https://www.ibge.gov.br.evil.test/','http://ibge.gov.br/','https://a@ibge.gov.br/','https://ibge.gov.br/?chave=x']:
            with self.subTest(fonte=fonte),self.assertRaises(ErroValidacao):validar_necessidade(necessidade(natureza='dado_publico',fonte_url=fonte))
    def test_entrada_territorial_fechada(self):
        for d in [necessidade(prioridade=True),necessidade(prioridade=4),necessidade(setor='outro'),necessidade(latitude=-23),necessidade(descricao='Nome e telefone 11999999999')]:
            with self.assertRaises(ErroValidacao):validar_necessidade(d)
    def test_filtro_exige_natureza_unica(self):
        self.assertEqual(filtros_territorio(MultiDict()),{'natureza':'simulado'})
        for f in [MultiDict([('natureza','simulado'),('natureza','dado_publico')]),MultiDict({'natureza':'todas'}),MultiDict({'municipio_id':'x'})]:
            with self.assertRaises(ErroValidacao):filtros_territorio(f)
    def test_geografia_rejeita_coordenada_invalida(self):
        with self.assertRaises(FonteIndisponivel):extrair_geografia({'features':[{'geometry':{'type':'Polygon','coordinates':[[[999,0],[1,2]]]}}]},3548708)
        g=extrair_geografia({'features':[{'geometry':{'type':'Polygon','coordinates':[[[-47,-24],[-46,-24],[-46,-23],[-47,-24]]]}}]},3548708)
        self.assertEqual(g['longitude'],-46.5)
