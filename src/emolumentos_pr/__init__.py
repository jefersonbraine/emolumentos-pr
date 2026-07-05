"""emolumentos-pr — cálculo de emolumentos de cartório do Paraná (FUNREJUS/VRCext)."""

from __future__ import annotations

from .calculo import calcular
from .erros import EmolumentoError, ValorForaDaTabela
from .modelos import (
    Ato,
    Componente,
    Faixa,
    ResultadoCalculo,
    TabelaEmolumentos,
    TipoAto,
)

__version__ = "0.1.0"

__all__ = [
    "Ato",
    "Componente",
    "EmolumentoError",
    "Faixa",
    "ResultadoCalculo",
    "TabelaEmolumentos",
    "TipoAto",
    "ValorForaDaTabela",
    "calcular",
    "__version__",
]
