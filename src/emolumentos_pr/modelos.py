"""Modelos de domínio da biblioteca.

Apenas ESTRUTURAS DE DADOS — nenhuma regra de cálculo. Toda quantia monetária
usa ``Decimal``, nunca ``float`` (float acumula erro de arredondamento,
inaceitável em cálculo legal).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class TipoAto(StrEnum):
    """Tipos de ato suportados.

    Divididos por REGIME de cálculo:
    - COM valor (emolumento pela tabela de faixas; Funrejus = 0,2% do valor):
      compra e venda, doação.
    - SEM valor (emolumento fixo; Funrejus = 25% do emolumento):
      escritura sem valor, procuração.
    """

    COMPRA_E_VENDA = "compra_e_venda"
    DOACAO = "doacao"
    SEM_VALOR = "sem_valor"
    PROCURACAO = "procuracao"

    @property
    def tem_valor(self) -> bool:
        return self in (TipoAto.COMPRA_E_VENDA, TipoAto.DOACAO)


@dataclass(frozen=True, slots=True)
class Faixa:
    """Faixa de valor do ato -> emolumento base daquela faixa, em VRCext.

    valor_min inclusivo; valor_max inclusivo (``None`` = "em diante").
    """

    valor_min: Decimal
    valor_max: Decimal | None
    emolumento_vrc: Decimal

    def contem(self, valor: Decimal) -> bool:
        if valor < self.valor_min:
            return False
        if self.valor_max is not None and valor > self.valor_max:
            return False
        return True


@dataclass(frozen=True, slots=True)
class TabelaEmolumentos:
    """Coleção ordenada de faixas para um tipo de ato com valor."""

    tipo: TipoAto
    faixas: tuple[Faixa, ...]

    def emolumento_vrc(self, valor: Decimal) -> Decimal:
        from .erros import ValorForaDaTabela

        for faixa in self.faixas:
            if faixa.contem(valor):
                return faixa.emolumento_vrc
        raise ValorForaDaTabela(valor=valor, tipo=self.tipo)


@dataclass(frozen=True, slots=True)
class Ato:
    """Um ato a calcular.

    - ``objetos``: valores dos imóveis/objetos (atos com valor). Vários objetos
      numa mesma escritura são tarifados um a um e depois somados.
    - ``usufruto``: doação com reserva de usufruto dobra o Funrejus.
    - ``partes_adicionais``: na procuração, pessoas além da 1ª de cada polo
      (cada uma soma 10 VRCext ao emolumento).
    """

    tipo: TipoAto
    objetos: tuple[Decimal, ...] = ()
    usufruto: bool = False
    partes_adicionais: int = 0


@dataclass(frozen=True, slots=True)
class Componente:
    """Uma linha do resultado (ex.: "Emolumentos", "Funrejus", "ISSQN")."""

    nome: str
    valor: Decimal


@dataclass(frozen=True, slots=True)
class ResultadoCalculo:
    """Resultado detalhado — sempre o breakdown, nunca só o total.

    ``total`` já vem quantizado em milésimos (o sistema do cartório trabalha em
    3 casas); os componentes guardam a precisão cheia usada na soma.
    """

    ato: Ato
    componentes: tuple[Componente, ...]
    total: Decimal
