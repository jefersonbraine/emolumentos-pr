"""Testes da MECÂNICA do motor (faixas, teto, multiobjeto, arredondamento)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from emolumentos_pr import Ato, TipoAto, calcular
from emolumentos_pr.erros import ValorForaDaTabela

D = Decimal


def _ato(*valores: str) -> Ato:
    return Ato(tipo=TipoAto.COMPRA_E_VENDA, objetos=tuple(D(v) for v in valores))


def _por_nome(resultado, nome: str) -> Decimal:
    return next(c.valor for c in resultado.componentes if c.nome == nome)


def test_seleciona_faixa_e_converte(tabela_sintetica, vrcext):
    # valor 3000 -> 2ª faixa (200 VRC) x R$1 = R$200 de emolumento.
    r = calcular(_ato("3000"), tabela_sintetica, vrcext)
    assert _por_nome(r, "Emolumentos") == D("200.00")


def test_limite_inferior_inclusivo(tabela_sintetica, vrcext):
    r = calcular(_ato("1000"), tabela_sintetica, vrcext)
    assert _por_nome(r, "Emolumentos") == D("100.00")


def test_fundep_e_issqn_sao_5pct_do_emolumento(tabela_sintetica, vrcext):
    r = calcular(_ato("3000"), tabela_sintetica, vrcext)  # emolumento 200
    assert _por_nome(r, "FUNDEP") == D("10.00")
    assert _por_nome(r, "ISSQN") == D("10.00")


def test_funrejus_com_valor_e_02pct(tabela_sintetica, vrcext):
    r = calcular(_ato("3000"), tabela_sintetica, vrcext)
    assert _por_nome(r, "Funrejus") == D("6.00")  # 0,2% de 3000


def test_multiobjeto_soma_por_objeto_e_selo_por_traslado(tabela_sintetica, vrcext):
    r = calcular(_ato("3000", "3000"), tabela_sintetica, vrcext)
    assert _por_nome(r, "Emolumentos") == D("400.00")        # 200 + 200
    assert _por_nome(r, "Selo") == D("24.00")                # 8 + 8*2
    assert _por_nome(r, "Distribuidor") == D("12.45")        # uma vez


def test_valor_fora_das_faixas(tabela_sintetica, vrcext):
    with pytest.raises(ValorForaDaTabela):
        calcular(Ato(tipo=TipoAto.COMPRA_E_VENDA, objetos=(D("-1"),)), tabela_sintetica, vrcext)


def test_usufruto_dobra_funrejus(tabela_sintetica, vrcext):
    base = calcular(_ato("3000"), tabela_sintetica, vrcext)
    doa = Ato(tipo=TipoAto.DOACAO, objetos=(D("3000"),), usufruto=True)
    r = calcular(doa, tabela_sintetica, vrcext)
    assert _por_nome(r, "Funrejus") == _por_nome(base, "Funrejus") * 2
