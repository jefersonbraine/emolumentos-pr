"""DADOS DA LEI e CONSTANTES do cálculo — a parte de domínio.

Fonte: Tabela XI (Atos dos Tabeliães) da tabela de emolumentos do PR.
Constantes e faixas transcritas da tabela oficial; os valores em R$ são a
VRCext (0,277) TRUNCADA em centavos — é assim que a própria tabela apresenta
(ex.: 1.485 x 0,277 = 411,345, mas a tabela mostra 411,34, não 411,35).

A tabela "não é progressiva": acha-se a faixa do valor do ato e aplica-se o
emolumento cheio daquela faixa (não se somam faixas).
"""

from __future__ import annotations

from decimal import Decimal

from .modelos import Faixa, TabelaEmolumentos, TipoAto

# --- Constantes (Tabela XI) -------------------------------------------------
ALIQUOTA_FUNREJUS = Decimal("0.002")        # atos com valor: 0,2% do valor
TETO_FUNREJUS = Decimal("7120.02")          # máximo de Funrejus por imóvel
PERC_FUNREJUS_SEM_VALOR = Decimal("0.25")   # atos sem valor: 25% do emolumento
ALIQUOTA_FUNDEP = Decimal("0.05")           # FUNDEP = 5% do emolumento
ALIQUOTA_ISSQN = Decimal("0.05")            # ISSQN  = 5% do emolumento
SELO_ESCRITURA = Decimal("8.00")            # selo da escritura (uma vez)
SELO_TRASLADO = Decimal("8.00")             # selo de traslado (por objeto)
DISTRIBUIDOR = Decimal("12.45")             # uma vez por escritura; 0 na procuração
TETO_EMOLUMENTO_VRC = Decimal("4972")       # emolumento máximo (R$ 1.377,24)

# Item IV: escritura sem valor = metade do item 1º (1.260 / 2 = 630 VRCext).
EMOLUMENTO_SEM_VALOR_VRC = Decimal("630")
# Item III: procuração base = 384,62 VRCext; +10 por outorgante/outorgado que acrescer.
EMOLUMENTO_PROCURACAO_VRC = Decimal("384.62")
VRC_POR_PARTE_ADICIONAL = Decimal("10")

# Item X.b: regra dos 80% aplica-se a PARTILHAS (divórcios e inventários) com
# mais de um bem — a unidade de maior valor a 100%, cada adicional (até 9) a 80%.
# NÃO se aplica a compra e venda / doação, que cobram 100% por imóvel. Constantes
# reservadas para o ato de partilha (v1.1). Item X.c (apartamento + garagem com
# matrícula autônoma a 50%) é outro ato, também v1.1.
PERC_UNIDADE_ADICIONAL = Decimal("0.80")
MAX_UNIDADES_ADICIONAIS = 9

# --- Tabela de faixas (valor do ato em R$ -> emolumento em VRCext) ----------
# Transcrita linha a linha da Tabela XI. Limites em R$ = limite VRCext x 0,277.
# A última faixa vai até "em diante" (o emolumento trava em 4.972 VRCext).
def _faixas_com_valor() -> tuple[Faixa, ...]:
    # (limite_superior_reais, emolumento_vrc)
    linhas = [
        ("15512.00", "1260"), ("18282.00", "1485"), ("21052.00", "1710"),
        ("23822.00", "1935"), ("26592.00", "2160"), ("29362.00", "2385"),
        ("32132.00", "2610"), ("34902.00", "2835"), ("37672.00", "3060"),
        ("40442.00", "3285"), ("43212.00", "3510"), ("45982.00", "3652"),
        ("48752.00", "3872"), ("51522.00", "4092"), ("54292.00", "4312"),
        ("57062.00", "4532"), ("59832.00", "4752"), ("62602.00", "4972"),
    ]
    faixas: list[Faixa] = []
    piso = Decimal("0")
    for i, (teto_str, vrc_str) in enumerate(linhas):
        ultima = i == len(linhas) - 1
        # Na última faixa, valor_max = None: tudo acima também trava em 4.972.
        teto = None if ultima else Decimal(teto_str)
        faixas.append(Faixa(piso, teto, Decimal(vrc_str)))
        piso = Decimal(teto_str) + Decimal("0.01")
    return tuple(faixas)


_FAIXAS = _faixas_com_valor()
COMPRA_E_VENDA = TabelaEmolumentos(tipo=TipoAto.COMPRA_E_VENDA, faixas=_FAIXAS)
DOACAO = TabelaEmolumentos(tipo=TipoAto.DOACAO, faixas=_FAIXAS)

TABELAS: dict[TipoAto, TabelaEmolumentos] = {
    TipoAto.COMPRA_E_VENDA: COMPRA_E_VENDA,
    TipoAto.DOACAO: DOACAO,
}


def tabela_de(tipo: TipoAto) -> TabelaEmolumentos:
    try:
        return TABELAS[tipo]
    except KeyError:
        raise NotImplementedError(
            f"'{tipo.value}' não usa tabela de faixas."
        ) from None
