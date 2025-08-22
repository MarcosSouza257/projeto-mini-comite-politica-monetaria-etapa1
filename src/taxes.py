from __future__ import annotations

from typing import Iterable, Tuple


def custody_rate_per_period(annual_fee: float, periods_per_year: int) -> float:
    """Equivalente por período para uma taxa de custódia anual.

    Ex.: 0,2% a.a. com períodos mensais (12): (1+0,002)^(1/12) - 1
    """
    return (1.0 + annual_fee) ** (1.0 / float(periods_per_year)) - 1.0


def custody_amount_for_period(balance_end: float, custody_rate_effective: float) -> float:
    """Calcula o valor da custódia do período a partir do saldo do fim do período."""
    return balance_end * custody_rate_effective


def compute_ir_final(vf_bruto: float, valor_inicial: float, ir_rate: float) -> float:
    """Calcula o IR final (tabela regressiva consolidada) sobre rendimentos.

    Fórmula: IR = ir_rate * max(0, vf_bruto - valor_inicial)
    """
    rendimento = max(0.0, vf_bruto - valor_inicial)
    return ir_rate * rendimento


def apply_custody_over_series(balances_end: Iterable[float], custody_rate_effective: float) -> Tuple[list, float]:
    """Aplica custódia período a período sobre uma série de saldos de fim de período.

    Retorna (custodias_por_periodo, custodia_total).
    """
    custodias = []
    total = 0.0
    for b in balances_end:
        c = custody_amount_for_period(b, custody_rate_effective)
        custodias.append(c)
        total += c
    return custodias, total


__all__ = [
    "custody_rate_per_period",
    "custody_amount_for_period",
    "compute_ir_final",
    "apply_custody_over_series",
]


