"""Roteiro personalizado dos 7 Passos (aula 3, Lucas Carmo - Vertex Club).

Estrutura e perguntas vem direto da aula (ver
docs/architecture/prospeccao-fanatica-schema.md#reuniaovenda); os
placeholders sao preenchidos com dados reais do lead e da configuracao de
produto - nada e inventado, so personalizado.
"""
from app.models.lead import Lead
from app.models.produto import ConfiguracaoProduto


def _v(value: str | None, fallback: str) -> str:
    return value if value else fallback


def gerar_roteiro(lead: Lead, produto: ConfiguracaoProduto) -> list[dict]:
    nome = _v(lead.nome, "a pessoa")
    empresa = _v(lead.empresa, "a empresa dela")
    territorio = _v(lead.territorio, "a regiao dela")
    vertical = _v(lead.vertical, "o mercado/ramo dela")

    produto_nome = _v(produto.nome_produto, "(configure o nome do produto em Configuracoes)")
    proposta = _v(produto.proposta_valor, "(configure a proposta de valor em Configuracoes)")
    dor = _v(produto.dor_resolvida, "(configure a dor que o produto resolve em Configuracoes)")
    preco = _v(produto.faixa_preco, "(configure a faixa de preco em Configuracoes)")
    entregaveis = [e for e in [produto.entregavel_1, produto.entregavel_2, produto.entregavel_3] if e]
    if not entregaveis:
        entregaveis = ["(configure ate 3 entregaveis-chave em Configuracoes)"]

    return [
        {
            "etapa": "apresentacao",
            "titulo": "1. Apresentacao",
            "objetivo": "Setar tom e autoridade. Reapresente-se mesmo que ja tenha se apresentado no assentamento.",
            "perguntas": [
                f"Oi {nome}, tudo bem? Antes de comecar, deixa eu me apresentar rapidinho de novo.",
                "Conte uma linha do tempo rapida: de onde voce veio, onde esta agora, pra onde vai com isso.",
            ],
        },
        {
            "etapa": "conexao",
            "titulo": "2. Conexao (15-20 min)",
            "objetivo": "Rapport profundo e descobrir onde voce vai gerar ROI. Fale menos, ouca mais.",
            "perguntas": [
                f"Me conta a historia de {empresa}: de onde veio, onde esta hoje em {territorio}, pra onde quer ir.",
                f"Ja pensou em ir alem do que faz hoje em {vertical}? (tecnica de suposicao - provoque uma crenca)",
                "Qual o maior gargalo hoje: time, processo ou receita?",
            ],
        },
        {
            "etapa": "decisao_imediata",
            "titulo": "3. DI - Decisao Imediata",
            "objetivo": "Fechar compromisso verbal ANTES do showtime. Sem isso, nao avance pro showtime.",
            "perguntas": [
                f"{nome}, posso contar com sua seriedade de me dar um sim ou um nao claro no final da nossa conversa?",
            ],
        },
        {
            "etapa": "showtime",
            "titulo": "4. Showtime (7-10 min)",
            "objetivo": "Apresentar com paixao, adaptado ao perfil dela. Menos e mais: mostre so 1 a 3 entregaveis.",
            "perguntas": [
                f"Visao: {produto_nome} resolve exatamente isso -> {dor}",
                f"Proposta de valor: {proposta}",
            ] + [f"Entregavel-chave: {e}" for e in entregaveis],
        },
        {
            "etapa": "fechamento",
            "titulo": "5. Fechamento",
            "objetivo": "Guiar a decisao com leveza: pre-fechamento -> ancoragem -> lembra a DI -> preco com silencio -> objecao -> celebra.",
            "perguntas": [
                "Tirando a questao financeira, isso faz sentido pra voce?",
                "(Ancoragem: compare com algo do MESMO mercado/ticket - cuidado pra nao 'viajar muito')",
                f"Lembra que voce topou me dar uma resposta clara? O investimento e {preco}.",
                "(Regra do silencio profundo: fale o preco uma vez e NAO fale mais nada depois. Quem falar primeiro perde.)",
            ],
        },
        {
            "etapa": "referidos",
            "titulo": "6. Referidos",
            "objetivo": "Pegue 5 a 10 indicacoes NA HORA, ainda na ligacao. Referido se pega, nao se pede.",
            "perguntas": [
                f"Antes de terminarmos, abre a agenda do seu celular comigo - quem mais em {vertical}/{territorio} tambem precisa disso?",
            ],
        },
        {
            "etapa": "validacao",
            "titulo": "7. Validacao",
            "objetivo": "Cada indicado recebe uma mensagem pre-pronta do indicador antes do seu contato frio.",
            "perguntas": [
                "Manda uma mensagem rapida pra eles agora avisando que eu vou entrar em contato?",
            ],
        },
    ]
