# upf_pr.py
"""UPF/PR — Unidade Padrão Fiscal do Paraná.

Indexador usado para corrigir taxas e multas estaduais, reajustado
periodicamente pela SEFA-PR conforme o IPCA. Usado aqui para o teto do
FUNREJUS (53 UPF/PR — Lei 21.180/2022, alterando o inciso VII do art. 3º
da Lei 12.216/1998, vigente desde 01/01/2023).

ATENÇÃO: revisar periodicamente. Confirmar no site da SEFA-PR
(sefanet.pr.gov.br) ou por reconciliação contra boleto real do TJPR.
"""
from decimal import Decimal

UPF_PR_ATUAL = Decimal("152.63")  # implícito por boleto real do TJPR, 17/08/2026