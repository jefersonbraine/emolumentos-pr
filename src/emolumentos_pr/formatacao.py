"""Formatação e parsing — a ponte entre a biblioteca e as interfaces.

O núcleo de cálculo só entende ``Decimal`` e só devolve ``ResultadoCalculo``.
Este módulo faz as duas pontas que toda interface (site, API, CLI) precisa:

  entrada:  texto do formulário  ──parse_valor──►  Decimal
  saída:    ResultadoCalculo     ──formatar────►  texto em R$  /  dict (JSON)

Fica separado do motor de propósito: **formatar não é calcular.** Assim o
cálculo permanece puro e reutilizável, e cada interface põe a sua casca por cima.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from .erros import ValorInvalido
from .modelos import ResultadoCalculo


# ---------------------------------------------------------------------------
# Entrada: o que o cliente digita -> Decimal
# ---------------------------------------------------------------------------
def parse_valor(texto: str) -> Decimal:
    """Converte o valor digitado pelo cliente em ``Decimal``.

    Aceita:
      - formato brasileiro:      "75.689,89"  (ponto = milhar, vírgula = decimal)
      - formato internacional:   "75689.89"
      - inteiro:                 "50000"

    Levanta ``ValorInvalido`` para texto não numérico, vazio ou valor negativo.

    Observação: para um valor inteiro grande, use dígitos puros ("75689") ou
    inclua a vírgula decimal. Uma entrada só com pontos e sem vírgula
    ("1.234.567") é ambígua e é rejeitada de propósito — melhor recusar do que
    adivinhar errado.
    """
    original = texto
    texto = texto.strip()
    if "," in texto:
        # BR: o ponto é separador de milhar; a vírgula é o decimal.
        texto = texto.replace(".", "").replace(",", ".")
    try:
        valor = Decimal(texto)
    except InvalidOperation:
        raise ValorInvalido(f"Valor inválido: {original!r}") from None
    if valor < 0:
        raise ValorInvalido("O valor não pode ser negativo.")
    return valor


# ---------------------------------------------------------------------------
# Saída: Decimal -> texto em R$
# ---------------------------------------------------------------------------
def formatar_brl(valor: Decimal, *, casas: int = 2) -> str:
    """Formata um ``Decimal`` como moeda brasileira: ``1694.794 -> 'R$ 1.694,79'``.

    ``casas=2`` (padrão) para exibir ao cliente em centavos; use ``casas=3`` para
    mostrar o valor exato em milésimos que o cartório usa internamente.
    """
    quant = Decimal(1).scaleb(-casas)  # 0.01 para 2 casas, 0.001 para 3
    q = valor.quantize(quant, rounding=ROUND_HALF_UP)
    # A f-string agrupa no padrão en-US ("1,694.79"); troca-se para o pt-BR.
    s = f"{q:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


# ---------------------------------------------------------------------------
# Saída: ResultadoCalculo -> dict (pronto para JSON)
# ---------------------------------------------------------------------------
def resultado_para_dict(resultado: ResultadoCalculo) -> dict:
    """Serializa o resultado num dicionário pronto para virar JSON.

    Regra de ouro: cada ``Decimal`` vira **string**, nunca ``float`` —
    converter para float reintroduziria o erro de arredondamento que a
    biblioteca evita com tanto cuidado. Junto vai a versão já formatada em R$,
    por conveniência do front-end.
    """
    return {
        "tipo": resultado.ato.tipo.value,
        "componentes": [
            {
                "nome": c.nome,
                "valor": str(c.valor),
                "valor_brl": formatar_brl(c.valor),
            }
            for c in resultado.componentes
        ],
        "total": str(resultado.total),
        "total_brl": formatar_brl(resultado.total),
    }
