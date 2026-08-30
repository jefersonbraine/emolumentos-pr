"""Motor de cálculo — funções PURAS que reproduzem os totais oficiais.

Ordem de arredondamento decifrada dos dados reais (é isto que faz os totais
baterem à casa do milésimo):
  1. Emolumento por objeto: VRC(faixa) x VRCext, TRUNCADO em CENTAVOS (ROUND_DOWN).
  2. FUNDEP/ISSQN/Funrejus: calculados sobre o emolumento em precisão CHEIA
     (não se arredonda antes de somar).
  3. Total: soma de tudo, quantizada em MILÉSIMOS com ROUND_HALF_UP (o sistema
     trabalha em 3 casas).
"""

from __future__ import annotations

from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

from emolumentos_pr.erros import EmolumentoError

from . import tabelas as t
from .modelos import Ato, Componente, ResultadoCalculo, TabelaEmolumentos, TipoAto
from .vrcext import VRCEXT_ATUAL

CENTAVO = Decimal("0.01")
MILESIMO = Decimal("0.001")


def _q(valor: Decimal, casas: Decimal) -> Decimal:
    return valor.quantize(casas, rounding=ROUND_HALF_UP)


def _emolumento_objeto(valor: Decimal, tabela: TabelaEmolumentos, vrcext: Decimal) -> Decimal:
    """Emolumento de um objeto: VRC da faixa (limitado ao teto) x VRCext.

    O emolumento é TRUNCADO em centavos (ROUND_DOWN), não arredondado — é assim
    que a Tabela XI apresenta (1.485 x 0,277 = 411,345 -> 411,34, não 411,35).
    """
    vrc = min(tabela.emolumento_vrc(valor), t.TETO_EMOLUMENTO_VRC)
    return (vrc * vrcext).quantize(CENTAVO, rounding=ROUND_DOWN)


def _funrejus_com_valor(valor: Decimal, *, usufruto: bool) -> Decimal:
    """0,2% do valor, teto R$ 7.120,02 por imóvel; dobra se houver usufruto."""
    base = min(valor * t.ALIQUOTA_FUNREJUS, t.TETO_FUNREJUS)
    return base * 2 if usufruto else base


def calcular(
    ato: Ato,
    tabela: TabelaEmolumentos | None = None,
    vrcext: Decimal = VRCEXT_ATUAL,
) -> ResultadoCalculo:
    """Calcula o resultado detalhado de um ato, com breakdown auditável."""
    if ato.tipo is TipoAto.DOACAO and ato.usufruto:
        return _calcular_doacao_usufruto(ato, tabela or t.tabela_de(ato.tipo), vrcext)
    if ato.tipo.tem_valor:
        return _calcular_com_valor(ato, tabela or t.tabela_de(ato.tipo), vrcext)
    return _calcular_sem_valor(ato, vrcext)


def _calcular_com_valor(ato: Ato, tabela: TabelaEmolumentos, vrcext: Decimal) -> ResultadoCalculo:
    """Compra e venda / doação. Com 2+ objetos, aplica o item X.b da Tabela XI
    automaticamente: o bem de maior valor paga emolumento integral (100%),
    cada bem adicional paga 80% — sem exceção, sem opção de desligar (reflete
    o comportamento confirmado do sistema oficial). Máximo 9 adicionais.
    """
    ordenados = sorted(ato.objetos, reverse=True)[: 1 + t.MAX_UNIDADES_ADICIONAIS]

    emolumento = Decimal("0")
    funrejus = Decimal("0")
    for i, valor in enumerate(ordenados):
        cheio = _emolumento_objeto(valor, tabela, vrcext)
        emolumento += cheio if i == 0 else cheio * t.PERC_UNIDADE_ADICIONAL
        funrejus += _funrejus_com_valor(valor, usufruto=ato.usufruto)

    n_obj = len(ordenados)
    selo = t.SELO_ESCRITURA + t.SELO_TRASLADO * n_obj

    componentes = _montar(
        emolumento=emolumento, funrejus=funrejus, selo=selo, distribuidor=t.DISTRIBUIDOR
    )
    return _finalizar(ato, componentes)


def _calcular_sem_valor(ato: Ato, vrcext: Decimal) -> ResultadoCalculo:
    if ato.tipo is TipoAto.PROCURACAO:
        vrc = t.EMOLUMENTO_PROCURACAO_VRC + ato.partes_adicionais * t.VRC_POR_PARTE_ADICIONAL
        distribuidor = Decimal("0")  # procuração não tem distribuidor
    else:  # SEM_VALOR
        vrc = t.EMOLUMENTO_SEM_VALOR_VRC
        distribuidor = t.DISTRIBUIDOR

    emolumento = (vrc * vrcext).quantize(CENTAVO, rounding=ROUND_DOWN)  # trunca, como a Tabela XI
    funrejus = emolumento * t.PERC_FUNREJUS_SEM_VALOR  # 25% do emolumento
    selo = t.SELO_ESCRITURA + t.SELO_TRASLADO  # escritura + 1 traslado

    componentes = _montar(
        emolumento=emolumento,
        funrejus=funrejus,
        selo=selo,
        distribuidor=distribuidor,
    )
    return _finalizar(ato, componentes)

def _calcular_doacao_usufruto(
        ato: Ato, 
        tabela: TabelaEmolumentos, 
        vrcext: Decimal
        ) -> ResultadoCalculo:
    """Doação com reserva de usufruto: dois atos jurídicos distintos dentro
    da mesma escritura (nua-propriedade + instituição de usufruto), desde a
    revogação do Ofício-Circular 35/2008 pelo Despacho 13298386-CJ.

    Cada ato cobra Emolumento sobre METADE do valor declarado; Funrejus é
    calculado sobre o valor TOTAL em cada ato (a soma equivale ao "Funrejus
    dobrado" do regime anterior); FUNDEP/ISSQN seguem o Emolumento de cada
    ato; Selo conta 1 escritura + 1 traslado por ato; Distribuidor é
    cobrado uma única vez.

    Reconciliado contra o sistema oficial do cartório em 30/08/2026, doação
    de R$ 100.000,00: Emolumentos 2.266,96 | Funrejus 400,00 | Selo 24,00 |
    Distribuidor 12,45 | FUNDEP/ISSQN 113,34 cada | Total 2.930,09
    (resíduo de milésimo, mesma classe do já documentado na procuração e
    na partilha).

    LIMITAÇÃO CONHECIDA: cobre só doação de um único bem, com usufruto
    sobre a integralidade dele. NÃO cobre (falta regra confirmada e caso
    real): múltiplos bens com usufruto simultâneo, usufruto parcial de um
    bem, ou combinação com a regra 100%/80% de partilha. Chamar esta
    função com mais de um objeto levanta erro de propósito.
    """
    if len(ato.objetos) != 1:
        raise EmolumentoError(
            "Doação com usufruto e múltiplos bens ainda não tem regra "
            "confirmada nesta biblioteca — informe um único objeto."
        )

    valor_total = ato.objetos[0]
    metade = valor_total / 2

    emol_ato = _emolumento_objeto(metade, tabela, vrcext)
    funrejus_ato = _funrejus_com_valor(valor_total, usufruto=False)  # Funrejus é sobre o total

    emolumento_total = emol_ato * 2  # dois atos jurídicos distintos
    funrejus_total = funrejus_ato * 2  # dois atos jurídicos distintos
    selo_total = t.SELO_ESCRITURA + t.SELO_TRASLADO * 2  # dois atos jurídicos distintos

    componentes = _montar(
        emolumento=emolumento_total,
        funrejus=funrejus_total,
        selo=selo_total,
        distribuidor=t.DISTRIBUIDOR
    )
    return _finalizar(ato, componentes)
 

def _montar(
    *, emolumento: Decimal, funrejus: Decimal, selo: Decimal, distribuidor: Decimal
) -> list[Componente]:
    """Monta o breakdown na ordem em que o sistema do cartório apresenta."""
    return [
        Componente("Emolumentos", emolumento),
        Componente("Funrejus", funrejus),
        Componente("Selo", selo),
        Componente("Distribuidor", distribuidor),
        Componente("FUNDEP", emolumento * t.ALIQUOTA_FUNDEP),
        Componente("ISSQN", emolumento * t.ALIQUOTA_ISSQN),
    ]


def _finalizar(ato: Ato, componentes: list[Componente]) -> ResultadoCalculo:
    total = _q(sum((c.valor for c in componentes), Decimal("0")), MILESIMO)
    return ResultadoCalculo(ato=ato, componentes=tuple(componentes), total=total)
