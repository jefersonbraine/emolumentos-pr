"""Interface de linha de comando — casca fina sobre a biblioteca (só stdlib)."""

from __future__ import annotations

import argparse

from .calculo import calcular
from .erros import EmolumentoError, ValorInvalido
from .formatacao import parse_valor
from .modelos import Ato, TipoAto


def _formatar(resultado) -> str:
    linhas = [f"Ato: {resultado.ato.tipo.value}", "-" * 34]
    for c in resultado.componentes:
        linhas.append(f"{c.nome:<20} R$ {c.valor:>12.3f}")
    linhas.append("-" * 34)
    linhas.append(f"{'TOTAL':<20} R$ {resultado.total:>12.3f}")
    return "\n".join(linhas)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="emolpr",
        description="Calculadora de emolumentos de cartório do Paraná (FUNREJUS/VRCext).",
    )

    sub = parser.add_subparsers(dest="comando", required=True)

    calc = sub.add_parser("calcular", help="Calcula o emolumento de um ato.")
    calc.add_argument("--tipo", required=True, choices=[x.value for x in TipoAto])
    calc.add_argument(
        "--valor",
        action="append",
        default=[],
        help="Valor de um objeto (repita --valor para vários imóveis na mesma escritura).",
    )
    calc.add_argument(
        "--usufruto",
        action="store_true",
        help="Doação com usufruto (dobra o Funrejus).",
    )
    calc.add_argument(
        "--partes",
        type=int,
        default=0,
        help="Procuração: partes além da 1ª de cada polo.",
    )

    args = parser.parse_args(argv)

    try:
        objetos = tuple(parse_valor(v) for v in args.valor)
    except ValorInvalido as exec:
        parser.error(str(exec))

    ato = Ato(
        tipo=TipoAto(args.tipo),
        objetos=objetos,
        usufruto=args.usufruto,
        partes_adicionais=args.partes,
    )
    try:
        resultado = calcular(ato)
    except (EmolumentoError, NotImplementedError) as exc:
        print(f"Erro: {exc}")
        return 1
    print(_formatar(resultado))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

