"""Casos REAIS do sistema do cartório — a prova de corretude do motor."""

from __future__ import annotations

from decimal import Decimal

import pytest

from emolumentos_pr import Ato, TipoAto, calcular

D = Decimal


def _cev(*valores: str) -> Ato:
    return Ato(tipo=TipoAto.COMPRA_E_VENDA, objetos=tuple(D(v) for v in valores))


def _por_nome(r, nome: str) -> Decimal:
    return next(c.valor for c in r.componentes if c.nome == nome)


@pytest.mark.parametrize(
    "ato,total_esperado",
    [
        (_cev("10000"), D("432.372")),
        (_cev("20000"), D("589.487")),
        (_cev("30000"), D("883.717")),
        (_cev("40000"), D("1109.384")),  # antes xfail; truncamento do emolumento resolveu
        (_cev("50000"), D("1375.278")),
        (_cev("60000"), D("1663.414")),   # emolumento no teto (4972 VRC)
        (_cev("70000"), D("1683.414")),   # teto: só o Funrejus sobe
        (_cev("700000"), D("2943.414")),  # teto: idem
    ],
)
def test_compra_e_venda_reconcilia_exato(ato, total_esperado):
    assert calcular(ato).total == total_esperado


def test_emolumento_40k_trunca_para_909_94():
    # 3.285 VRC x 0,277 = 909,945 -> TRUNCA -> 909,94 (não 909,95).
    assert _por_nome(calcular(_cev("40000")), "Emolumentos") == D("909.94")


def test_multiobjeto_dois_terrenos():
    # 50.000 + 30.000: emolumento/funrejus por objeto, distribuidor uma vez,
    # selo 8 (escritura) + 8x2 (traslados) = 24. Em CEV/doação cada imóvel é
    # cobrado a 100% (a regra dos 80% é de partilha: divórcio/inventário).
    ato = Ato(tipo=TipoAto.COMPRA_E_VENDA, objetos=(D("50000"), D("30000")))
    assert calcular(ato).total == D("2238.545")


def test_escritura_sem_valor():
    assert calcular(Ato(tipo=TipoAto.SEM_VALOR)).total == D("264.039")


def test_procuracao_base_emolumento():
    # Tabela XI item III: 384,62 VRC -> 106,5397 -> TRUNCA -> 106,53.
    assert _por_nome(calcular(Ato(tipo=TipoAto.PROCURACAO)), "Emolumentos") == D("106.53")


def test_procuracao_parte_adicional_soma_2_77():
    base = _por_nome(calcular(Ato(tipo=TipoAto.PROCURACAO)), "Emolumentos")
    com_parte = _por_nome(
        calcular(Ato(tipo=TipoAto.PROCURACAO, partes_adicionais=1)), "Emolumentos"
    )
    assert com_parte - base == D("2.77")  # 10 VRC x 0,277


@pytest.mark.xfail(reason="Resíduo ~0,003 no total; exemplos de sem-valor e procuração "
                          "discordam na 3ª casa do arredondamento do Funrejus de 25%.")
def test_procuracao_total():
    assert calcular(Ato(tipo=TipoAto.PROCURACAO)).total == D("159.813")
