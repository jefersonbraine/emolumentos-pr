"""Playground da emolumentos-pr — experimente no terminal.

Rode:
    python experimentar.py

Digite valores em QUALQUER formato:  75689,89   75.689,89   75689.89
Digite 'sair' em qualquer pergunta para encerrar.
"""

from __future__ import annotations

import json

from emolumentos_pr import (
    Ato,
    TipoAto,
    calcular,
    formatar_brl,
    parse_valor,
    resultado_para_dict,
)
from emolumentos_pr.erros import EmolumentoError

# Valores reais do sistema, para você conferir que o cálculo bate.
CASOS_REFERENCIA = """
CASOS DE REFERÊNCIA (confira que batem):
  compra e venda  R$ 40.000         -> Total R$ 1.109,384
  compra e venda  R$ 50.000         -> Total R$ 1.375,278
  compra e venda  R$ 60.000 (teto)  -> Total R$ 1.663,414
  2 imóveis 50.000 + 30.000         -> Total R$ 2.238,545
  escritura sem valor               -> Total R$ 264,039
"""

MENU = {
    "1": TipoAto.COMPRA_E_VENDA,
    "2": TipoAto.DOACAO,
    "3": TipoAto.SEM_VALOR,
    "4": TipoAto.PROCURACAO,
}


class Sair(Exception):
    """Levantada quando o usuário digita 'sair'."""


def perguntar(prompt: str) -> str:
    resposta = input(prompt)
    if resposta.strip().lower() in ("sair", "q", "quit", "exit"):
        raise Sair
    return resposta


def ler_valores() -> tuple:
    bruto = perguntar("  Valor(es) do(s) imóvel(is) [separe vários por espaço]: ")
    valores = tuple(parse_valor(p) for p in bruto.split())  # parse_valor valida cada um
    if not valores:
        raise EmolumentoError("Nenhum valor informado.")
    return valores


def montar_ato() -> Ato:
    print("\n  Tipo:  1) compra e venda   2) doação   3) sem valor   4) procuração")
    tipo = MENU.get(perguntar("  Escolha (1-4): ").strip())
    if tipo is None:
        raise EmolumentoError("Opção inválida (use 1 a 4).")

    if tipo.tem_valor:
        objetos = ler_valores()
        usufruto = False
        if tipo is TipoAto.DOACAO:
            usufruto = perguntar("  Com usufruto? (s/N): ").strip().lower() == "s"
        return Ato(tipo=tipo, objetos=objetos, usufruto=usufruto)

    partes = 0
    if tipo is TipoAto.PROCURACAO:
        bruto = perguntar("  Partes adicionais (0 se só uma de cada lado): ").strip()
        partes = int(bruto) if bruto.isdigit() else 0
    return Ato(tipo=tipo, partes_adicionais=partes)


def mostrar(ato: Ato) -> None:
    r = calcular(ato)
    print("\n  " + "-" * 36)
    for c in r.componentes:
        print(f"  {c.nome:<14}{formatar_brl(c.valor, casas=3):>20}")
    print("  " + "-" * 36)
    print(f"  {'TOTAL (exato)':<14}{formatar_brl(r.total, casas=3):>20}")
    print(f"  {'Cobrado (R$)':<14}{formatar_brl(r.total):>20}")
    print("  " + "-" * 36)


def main() -> None:
    print("=" * 40)
    print("  PLAYGROUND — emolumentos-pr")
    print("=" * 40)
    print(CASOS_REFERENCIA)
    print("  (digite 'sair' em qualquer pergunta para encerrar)")

    while True:
        try:
            ato = montar_ato()
            mostrar(ato)
            if perguntar("\n  Ver o JSON (para API)? (s/N): ").strip().lower() == "s":
                print(json.dumps(resultado_para_dict(calcular(ato)), indent=2, ensure_ascii=False))
        except Sair:
            print("\n  Até logo!")
            break
        except (EOFError, KeyboardInterrupt):
            print("\n  Até logo!")
            break
        except EmolumentoError as e:
            print(f"  ⚠  {e}")  # entrada inválida, valor fora da tabela, etc.
        print()


if __name__ == "__main__":
    main()
