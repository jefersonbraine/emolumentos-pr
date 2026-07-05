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