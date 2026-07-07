"""emolumentos-pr — cálculo de emolumentos de cartório do Paraná (FUNREJUS/VRCext)."""

from __future__ import annotations

from .calculo import calcular
from .erros import EmolumentoError, ValorForaDaTabela, ValorInvalido
from .formatacao import formatar_brl, parse_valor, resultado_para_dict
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
    "ValorInvalido",
    "calcular",
    "formatar_brl",
    "parse_valor",
    "resultado_para_dict",
    "__version__",
]
