"""Fixtures dos testes de mecânica (independentes dos números da lei)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from emolumentos_pr.modelos import Faixa, TabelaEmolumentos, TipoAto

@pytest.fixture
def tabela_sintetica() -> TabelaEmolumentos:
    # Faixas simples e redondas: os testes de mecânica não dependem da lei real.
    return TabelaEmolumentos(
        tipo=TipoAto.COMPRA_E_VENDA,
        faixas=(
            Faixa(Decimal("0"), Decimal("1000"), Decimal("100")),
            Faixa(Decimal("1000.01"), Decimal("5000"), Decimal("200")),
            Faixa(Decimal("5000.01"), None, Decimal("300")),
        ),
    )

@pytest.fixture
def vrcext() -> Decimal:
    return Decimal("1.00")  # 1 VRC = R$ 1,00 nos testes de mecânica