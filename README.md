<div align="center">
  <img src="https://raw.githubusercontent.com/jefersonbraine/emolumentos-pr/main/docs/assets/Banner%20-%20emolumentos-pr.png" alt="Emolumentos PR Banner" width="1920" />


![CI](https://github.com/jefersonbraine/emolumentos-pr/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
<!-- ![PyPI](https://img.shields.io/pypi/v/emolumentos-pr.svg) -->

Biblioteca Python para cálculo de **emolumentos de cartório do Paraná**, indexados
por **VRCext**, conforme a **Lei Estadual PR nº 21.869/2023** (FUNREJUS).

Entra o tipo de ato e o valor da transação; sai o emolumento detalhado, com o
breakdown de cada componente — não apenas o total.

> **Status:** `0.1.0` — alpha. O motor de cálculo está pronto; as tabelas da lei
> e o valor da VRCext ainda são placeholders (veja [Roadmap](#roadmap)). **Os
> números só têm validade legal depois de preenchidos os dados oficiais.**

## Por que isto não é trivial

Calcular emolumento não é "multiplicar por uma alíquota". A regra do PR envolve
faixas de valor do ato, indexação por uma unidade estadual (VRCext) que é
reajustada periodicamente, e componentes acessórios (FUNREJUS, ISS, taxas). O
mesmo conjunto de documentos apresentado por um cliente pode servir a atos
diferentes, com emolumentos diferentes. Traduzir esse emaranhado
jurídico-financeiro em código correto e testado é o objetivo desta biblioteca.

## Instalação

```bash
pip install emolumentos-pr        # (após publicação no PyPI)
# ou, em desenvolvimento:
pip install -e ".[dev]"
```

## Uso

Como biblioteca:

```python
from decimal import Decimal
from emolumentos_pr import Ato, TipoAto, calcular
from emolumentos_pr.tabelas import tabela_de
from emolumentos_pr.vrcext import VRCEXT_ATUAL

ato = Ato(tipo=TipoAto.COMPRA_E_VENDA, valor=Decimal("250000.00"))
resultado = calcular(ato, tabela_de(ato.tipo), VRCEXT_ATUAL)

print(resultado.total)
for componente in resultado.componentes:
    print(componente.nome, componente.valor)
```

Pela linha de comando:

```bash
emolpr calcular --tipo compra_e_venda --valor 250000.00
```

## Decisões de design

Escolhas deliberadas — cada uma tem um porquê que vale saber explicar:

- **`Decimal` em todo valor monetário, nunca `float`.** Float acumula erro de
  arredondamento; inaceitável em cálculo financeiro/legal.
- **Núcleo sem dependências.** O pacote instala e roda só com a biblioteca
  padrão. A CLI usa `argparse`.
- **Cálculo em funções puras.** A regra de negócio não faz I/O e não guarda
  estado — mesma entrada, mesma saída. Isso é o que torna a suíte de testes
  confiável.
- **Resultado sempre auditável.** O retorno traz o breakdown de componentes, não
  só a soma — dá para ver de onde veio cada centavo.
- **Dados da lei isolados.** Tabelas e VRCext ficam em módulos próprios; atualizar
  a lei é editar dado, não caçar número mágico no meio da lógica.

## Roadmap

**v0.1 (COMPLETO):**
- [x] Motor de cálculo (faixas, indexação por VRCext, truncamento, breakdown)
- [x] Empacotamento, CI e testes do motor
- [x] Tabela XI completa de faixas (valor -> VRCext) em `tabelas.py`
- [x] VRCext oficial (0,277) em `vrcext.py`
- [x] Componentes: Funrejus (0,2% e 25%), FUNDEP, ISSQN, Selo, Distribuidor
- [x] Compra e venda, doação (com/sem usufruto), escritura sem valor, procuração
- [x] Multiobjeto em CEV/doação (100% por imóvel)
- [x] Casos oficiais reconciliando à casa do milésimo em `tests/`

Todos os atos do escopo v1 reproduzem o sistema do cartório, para qualquer valor.

**Atos previstos para o v1.1** (a estrutura já suporta; falta o dado e um
exemplo real para reconciliar cada um):
- **Partilha (divórcio/inventário)** — item X.b: bem de maior valor a 100%,
  cada adicional (até nove) a 80%.
- **Apartamento + garagem com matrícula autônoma** — item X.c: garagem a 50%.
- Demais atos da Tabela XI: reconhecimento de firma, autenticação, testamentos,
  atas notariais, certidões, pública forma, buscas.

**Resíduo conhecido:** o total da procuração fecha a ~0,003 (os exemplos de
sem-valor e procuração discordam na 3ª casa do arredondamento do Funrejus de
25%). Um printout novo do sistema pina a regra.

**Fora do escopo (propositalmente):** interface web, front-end, banco de dados,
múltiplos estados.

## Licença

MIT — veja [LICENSE](LICENSE).
