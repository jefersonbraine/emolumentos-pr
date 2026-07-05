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
    if ato.tipo.tem_valor:
        return _calcular_com_valor(ato, tabela or t.tabela_de(ato.tipo), vrcext)
    return _calcular_sem_valor(ato, vrcext)


def _calcular_com_valor(ato: Ato, tabela: TabelaEmolumentos, vrcext: Decimal) -> ResultadoCalculo:
    emolumento = sum((_emolumento_objeto(v, tabela, vrcext) for v in ato.objetos), Decimal("0"))
    funrejus = sum(
        (_funrejus_com_valor(v, usufruto=ato.usufruto) for v in ato.objetos), Decimal("0")
    )
    n_obj = len(ato.objetos)
    selo = t.SELO_ESCRITURA + t.SELO_TRASLADO * n_obj

    componentes = _montar(
        emolumento=emolumento,
        funrejus=funrejus,
        selo=selo,
        distribuidor=t.DISTRIBUIDOR,
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
