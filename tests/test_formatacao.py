"""Testes do módulo de formatação e parsing."""

from __future__ import annotations

from decimal import Decimal

import pytest

from emolumentos_pr import (
    Ato,
    TipoAto,
    calcular,
    formatar_brl,
    parse_valor,
    resultado_para_dict,
)
from emolumentos_pr.erros import ValorInvalido

D = Decimal


# --- parse_valor -----------------------------------------------------------
@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("75689,89", D("75689.89")),      # BR com centavos
        ("75.689,89", D("75689.89")),     # BR com milhar
        ("75689.89", D("75689.89")),      # internacional
        ("50000", D("50000")),            # inteiro
        ("  50000  ", D("50000")),        # com espaços
        ("1.234.567,89", D("1234567.89")),# BR grande
    ],
)
def test_parse_valor_aceita_formatos(entrada, esperado):
    assert parse_valor(entrada) == esperado


@pytest.mark.parametrize("entrada", ["abc", "", "  ", "-100", "10,5,5"])
def test_parse_valor_rejeita_invalido(entrada):
    with pytest.raises(ValorInvalido):
        parse_valor(entrada)


# --- formatar_brl ----------------------------------------------------------
@pytest.mark.parametrize(
    "valor,esperado",
    [
        ("1694.794", "R$ 1.694,79"),
        ("264.039", "R$ 264,04"),
        ("50", "R$ 50,00"),
        ("1234567.89", "R$ 1.234.567,89"),
        ("0", "R$ 0,00"),
    ],
)
def test_formatar_brl_padrao_centavos(valor, esperado):
    assert formatar_brl(D(valor)) == esperado


def test_formatar_brl_em_milesimos():
    assert formatar_brl(D("1694.794"), casas=3) == "R$ 1.694,794"


# --- resultado_para_dict ---------------------------------------------------
def test_resultado_para_dict_serializa_para_json():
    ato = Ato(tipo=TipoAto.COMPRA_E_VENDA, objetos=(D("40000"),))
    d = resultado_para_dict(calcular(ato))

    assert d["tipo"] == "compra_e_venda"
    assert d["total"] == "1109.384"          # Decimal vira STRING, não float
    assert isinstance(d["total"], str)
    assert d["total_brl"] == "R$ 1.109,38"
    assert d["componentes"][0]["nome"] == "Emolumentos"
    assert d["componentes"][0]["valor"] == "909.94"
    assert d["componentes"][0]["valor_brl"] == "R$ 909,94"


def test_dict_nunca_usa_float():
    # Garante que nenhum valor serializado é float (preserva a precisão).
    d = resultado_para_dict(calcular(Ato(tipo=TipoAto.SEM_VALOR)))
    assert isinstance(d["total"], str)
    assert all(isinstance(c["valor"], str) for c in d["componentes"])
