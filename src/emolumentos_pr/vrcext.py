"""VRCext — a unidade de indexação usada pela tabela de emolumentos do PR.

Isolar este valor num único lugar é uma decisão de design deliberada: quando a
VRCext for reajustada, a atualização é UMA linha aqui, e não uma caça ao tesouro
por números mágicos espalhados pelo código.
"""

from __future__ import annotations

from decimal import Decimal

# Valor corrente da VRCext, decifrado dos dados reais do sistema do cartório:
#   Emolumento = VRC(faixa) x 0,277  (ex.: 1260 x 0,277 = 349,020).
# TODO(voce): confirmar a fonte/data oficial deste valor e registrar aqui, para
# rastreabilidade legal.
VRCEXT_ATUAL: Decimal = Decimal("0.277")