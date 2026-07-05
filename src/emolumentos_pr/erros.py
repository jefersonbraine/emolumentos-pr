"""Exceções da biblioteca.

Ter exceções próprias (em vez de ValueError genérico) permite que quem usa a
biblioteca capture exatamente o erro que quer tratar, e deixa as mensagens
consistentes.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .modelos import TipoAto


class EmolumentoError(Exception):
    """Base de todos os erros da biblioteca."""


class ValorForaDaTabela(EmolumentoError):
    """Nenhuma faixa da tabela cobre o valor informado."""

    def __init__(self, valor: Decimal, tipo: TipoAto) -> None:
        self.valor = valor
        self.tipo = tipo
        super().__init__(
            f"Valor {valor} não se enquadra em nenhuma faixa da tabela de "
            f"'{tipo.value}'. Verifique se a última faixa cobre 'em diante'."
        )
