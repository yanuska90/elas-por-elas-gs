import unittest
from elas.validacao import validar_anuncio, ErroValidacao


def exemplo(**alteracoes):
    dados = {'titulo':'Livros de demonstração','tipo':'doacao','categoria':'itens',
             'descricao':'Exemplo fictício de livros para uma atividade comunitária.',
             'contrapartida':'','municipio_id':3548708,'status':'aberto'}
    dados.update(alteracoes)
    return dados


class TestValidacao(unittest.TestCase):
    def test_aceita_dados_validos(self):
        self.assertEqual(validar_anuncio(exemplo())['tipo'],'doacao')

    def test_rejeita_objeto_incorreto(self):
        for dados in ([],None,42,'texto'):
            with self.subTest(dados=dados), self.assertRaises(ErroValidacao):
                validar_anuncio(dados)

    def test_rejeita_campos_ausentes_e_extras(self):
        for dados in ({'titulo':'Algo'},exemplo(senha='indevida')):
            with self.assertRaises(ErroValidacao): validar_anuncio(dados)

    def test_rejeita_html_contatos_e_documentos(self):
        for texto in ('<script>alert(1)</script>','Contato: pessoa@example.com','Telefone: (11) 99999-9999','Visite https://example.com'):
            with self.subTest(texto=texto), self.assertRaises(ErroValidacao):
                validar_anuncio(exemplo(descricao=texto))

    def test_rejeita_booleano_como_numero(self):
        with self.assertRaises(ErroValidacao): validar_anuncio(exemplo(municipio_id=True))

    def test_rejeita_tipo_invalido_e_campo_muito_longo(self):
        for dados in (exemplo(tipo=[]),exemplo(categoria='saude'),exemplo(titulo='x'*101)):
            with self.assertRaises(ErroValidacao): validar_anuncio(dados)

    def test_permuta_exige_contrapartida(self):
        with self.assertRaises(ErroValidacao): validar_anuncio(exemplo(tipo='permuta'))
        self.assertEqual(validar_anuncio(exemplo(tipo='permuta',contrapartida='Aulas de costura'))['tipo'],'permuta')

    def test_pedido_nao_exige_contrapartida(self):
        with self.assertRaises(ErroValidacao): validar_anuncio(exemplo(tipo='pedido',contrapartida='Uma troca'))

    def test_edicao_exige_versao(self):
        with self.assertRaises(ErroValidacao): validar_anuncio(exemplo(),edicao=True)
        self.assertEqual(validar_anuncio(exemplo(versao=1),edicao=True)['versao'],1)
