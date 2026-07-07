<div align="center">
  <img src="https://raw.githubusercontent.com/jefersonbraine/emolumentos-pr/main/docs/assets/Banner%20-%20emolumentos-pr.png" alt="Emolumentos PR Banner" width="1920" />

  ![CI](https://github.com/jefersonbraine/emolumentos-pr/actions/workflows/ci.yml/badge.svg)
  ![PyPI](https://img.shields.io/pypi/v/emolumentos-pr.svg)
  ![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
  ![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
  ![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
</div>

Biblioteca Python para cálculo de **emolumentos de cartório do Paraná**, indexados
por **VRCext**, conforme a **Lei Estadual PR nº 21.869/2023** (FUNREJUS).

Entra o tipo de ato e o valor da transação; sai o emolumento detalhado, com o
breakdown de cada componente — não apenas o total.

> **Status:** `0.2.1` — funcional. Motor completo, com a **Tabela XI** oficial e o
> valor real da VRCext. Compra e venda, doação (com/sem usufruto), escritura sem
> valor e procuração **reconciliam com o sistema do cartório à casa do milésimo**.

## Por que isto não é trivial

Calcular emolumento não é "multiplicar por uma alíquota". A regra do PR envolve
faixas de valor do ato, indexação por uma unidade estadual (VRCext) que é
reajustada periodicamente, um teto legal e componentes acessórios (FUNREJUS,
FUNDEP, ISSQN, selo, distribuidor) — cada um com sua própria lógica. O mesmo
conjunto de documentos apresentado por um cliente pode servir a atos diferentes,
com emolumentos diferentes. Traduzir esse emaranhado jurídico-financeiro em
código correto e testado é o objetivo desta biblioteca.

## Instalação

```bash
pip install emolumentos-pr
# ou, em desenvolvimento:
pip install -e ".[dev]"
```

## Uso

Como biblioteca:

```python
from decimal import Decimal
from emolumentos_pr import Ato, TipoAto, calcular

ato = Ato(tipo=TipoAto.COMPRA_E_VENDA, objetos=(Decimal("250000"),))
resultado = calcular(ato)

print(resultado.total)                     # Decimal('2043.414')
for componente in resultado.componentes:
    print(componente.nome, componente.valor)
```

Vários imóveis na mesma escritura, doação com usufruto e procuração:

```python
# dois imóveis (cada um a 100%; distribuidor uma vez; selo por traslado)
calcular(Ato(tipo=TipoAto.COMPRA_E_VENDA, objetos=(Decimal("50000"), Decimal("30000"))))

# doação com usufruto (dobra o Funrejus)
calcular(Ato(tipo=TipoAto.DOACAO, objetos=(Decimal("80000"),), usufruto=True))

# procuração com partes que acrescem
calcular(Ato(tipo=TipoAto.PROCURACAO, partes_adicionais=2))
```

Entrada e saída para interfaces (web/API):

```python
from emolumentos_pr import parse_valor, formatar_brl, resultado_para_dict

valor = parse_valor("250.000,00")          # aceita formato brasileiro e internacional
resultado = calcular(Ato(tipo=TipoAto.COMPRA_E_VENDA, objetos=(valor,)))

formatar_brl(resultado.total)              # "R$ 2.043,41"
resultado_para_dict(resultado)             # dict pronto para JSON (Decimal como string)
```

Pela linha de comando (aceita vírgula ou ponto):

```bash
emolpr calcular --tipo compra_e_venda --valor 250000
emolpr calcular --tipo compra_e_venda --valor 50000 --valor 30000   # dois imóveis
emolpr calcular --tipo doacao --valor 80000 --usufruto
emolpr calcular --tipo procuracao --partes 2
emolpr calcular --tipo sem_valor
```

## Decisões de design

Escolhas deliberadas — cada uma tem um porquê que vale saber explicar:

- **`Decimal` em todo valor monetário, nunca `float`.** Float acumula erro de
  arredondamento; inaceitável em cálculo financeiro/legal.
- **Truncamento fiel à Tabela XI.** O emolumento é truncado em centavos (não
  arredondado), como a tabela oficial faz — é o que faz os totais baterem.
- **Núcleo sem dependências.** O pacote instala e roda só com a biblioteca
  padrão. A CLI usa `argparse`.
- **Cálculo em funções puras.** A regra de negócio não faz I/O e não guarda
  estado — mesma entrada, mesma saída. Isso é o que torna a suíte de testes
  confiável.
- **Resultado sempre auditável.** O retorno traz o breakdown de componentes, não
  só a soma — dá para ver de onde veio cada centavo.
- **Dados da lei isolados.** Tabelas e VRCext ficam em módulos próprios; atualizar
  a lei é editar dado, não caçar número mágico no meio da lógica.
- **Formatar não é calcular.** Parsing de entrada e formatação em R$/JSON vivem
  no módulo `formatacao`, separados do motor — cada interface põe a sua casca.

## Documentação

- [`docs/COMO_FUNCIONA.md`](docs/COMO_FUNCIONA.md) — guia de arquitetura: o
  domínio, cada módulo, as fórmulas e as decisões de design.
- [`examples/experimentar.py`](examples/experimentar.py) — playground interativo
  no terminal.

## Roadmap

**Implementado:**
- [x] Motor de cálculo (faixas, indexação por VRCext, truncamento, breakdown)
- [x] Tabela XI completa de faixas e VRCext oficial (0,277)
- [x] Componentes: Funrejus (0,2% e 25%), FUNDEP, ISSQN, Selo, Distribuidor
- [x] Compra e venda, doação (com/sem usufruto), escritura sem valor, procuração
- [x] Multiobjeto em CEV/doação (100% por imóvel)
- [x] Módulo `formatacao` (parse de entrada BR, formatação R$, serialização JSON)
- [x] CLI aceitando formato brasileiro
- [x] Empacotamento, CI e publicação automatizada no PyPI
- [x] Casos oficiais reconciliando à casa do milésimo em `tests/`

**Previsto (a estrutura já suporta; falta o dado e um exemplo real para
reconciliar cada um):**
- **Partilha (divórcio/inventário)** — item X.b: bem de maior valor a 100%,
  cada adicional (até nove) a 80%.
- **Apartamento + garagem com matrícula autônoma** — item X.c: garagem a 50%.
- **Testamento** — modalidades (público, cerrado, revogação) com valores próprios.
- Demais atos da Tabela XI: reconhecimento de firma, autenticação, atas
  notariais, certidões, pública forma, buscas.

**Resíduo conhecido:** o total da procuração fecha a ~0,003 (os exemplos de
sem-valor e procuração discordam na 3ª casa do arredondamento do Funrejus de
25%). Um printout novo do sistema pina a regra.

**Fora do escopo (propositalmente):** interface web pronta, front-end, banco de
dados, múltiplos estados. O módulo `formatacao` prepara o terreno para
interfaces, mas a biblioteca em si é só o motor de cálculo.

## Licença

MIT — veja [LICENSE](LICENSE).
