"""Vocabulário único para formulários, validação, ODS e diagnóstico territorial.

As relações com ODS expressam contribuições pretendidas, não impacto comprovado.
Yanuska Monalisa Antunes Yabiku - RM 571686.
"""
CATEGORIAS_INFO = {
 'alimentos': ('Doação de alimentos', [2,10,12], 'Cestas, hortifrúti e pedidos de alimentação. Receber apoio não exige troca.'),
 'excedentes': ('Excedentes de restaurantes', [2,12], 'Informe quantidade, prazo, conservação e alergênicos. O cadastro não certifica segurança sanitária.'),
 'marmitas': ('Marmitas solidárias', [2,10], 'Organize porções e janela de disponibilidade com uma organização receptora.'),
 'itens': ('Doações e itens essenciais', [10,12], 'Roupas, livros, materiais e utensílios em condições de uso.'),
 'aprendizagem': ('Educação e aprendizagem', [4,10], 'Aulas, idiomas, inclusão digital e materiais educativos.'),
 'trabalho': ('Vagas e preparação profissional', [8,10], 'Vagas fictícias, currículo, entrevistas e oportunidades de renda; sem promessa de contratação.'),
 'juridico': ('Apoio jurídico e direitos', [10,16], 'Encaminhamento informativo. Não publique documentos, processos ou relatos pessoais.'),
 'saude': ('Saúde e acolhimento', [3,10], 'Informação e encaminhamento a serviços; sem diagnóstico ou dados clínicos.'),
 'cuidados': ('Cuidado pessoal e bem-estar', [3,5,10], 'Doação de tempo ou permuta voluntária de cuidados, respeitando escolhas e qualificações.'),
 'lazer': ('Lazer, cultura e convivência', [3,11], 'Atividades comunitárias e acesso à cultura, sem cadastro de crianças.'),
 'caronas': ('Caronas solidárias', [10,11], 'Regiões aproximadas, horário e lugares. Não publique endereços residenciais.'),
 'reciclaveis': ('Materiais recicláveis', [11,12], 'Separe materiais e combine aceitação e coleta com o operador.'),
 'oleo': ('Óleo de cozinha usado', [6,12], 'Óleo frio em recipiente fechado; destinação a ponto de coleta, sem descarte na pia.'),
 'compostagem': ('Orgânicos e composteiras', [12,13], 'Resíduos separados dependem de aceitação e processamento. Resíduo não é adubo pronto.'),
 'hortas': ('Hortas e composto maturado', [2,11,12], 'Mudas, cultivo e composto adequado ao uso, com orientação do responsável.'),
}
ALIMENTARES = {'alimentos','excedentes','marmitas'}
AMBIENTAIS = {'reciclaveis','oleo','compostagem','hortas'}
SETORES = {
 'educacao': ('Educação',[4,10],'Avaliar ampliação de atividades educativas e inclusão digital.'),
 'seguranca': ('Segurança e convivência',[11,16],'Avaliar iluminação, espaços públicos e prevenção comunitária.'),
 'alimentacao': ('Alimentação',[2,12],'Avaliar cozinha solidária e articulação para aproveitamento de alimentos.'),
 'moradia': ('Moradia',[10,11],'Avaliar acesso a programas habitacionais e orientação pública.'),
 'saneamento': ('Saneamento',[6,11],'Avaliar água, esgoto, drenagem e gestão de resíduos.'),
 'transporte': ('Transporte',[10,11],'Avaliar acessibilidade, cobertura e horários de transporte.'),
 'saude': ('Saúde',[3,10],'Avaliar acolhimento e acesso aos serviços de saúde.'),
 'lazer': ('Lazer e cultura',[3,11],'Avaliar atividades culturais e espaços de convivência.'),
 'ambiente': ('Meio ambiente',[12,13],'Avaliar coleta seletiva, óleo e compostagem comunitária.'),
 'trabalho': ('Trabalho e renda',[8,10],'Avaliar formação, orientação profissional e oportunidades.'),
}

def catalogo_publico():
    return {'categorias':[{'id':k,'nome':v[0],'ods':v[1],'orientacao':v[2]} for k,v in CATEGORIAS_INFO.items()],
            'setores':[{'id':k,'nome':v[0],'ods':v[1],'proposta':v[2]} for k,v in SETORES.items()]}
