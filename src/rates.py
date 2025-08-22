from __future__ import annotations

from typing import Iterable, List


# ------------------------------
# Conversões de taxas
# ------------------------------
def annual_to_monthly(i_a: float) -> float:
    """Converte taxa efetiva anual em taxa efetiva mensal.

    Ex.: 15% a.a. -> (1+0,15)^(1/12) - 1
    """
    return (1.0 + i_a) ** (1.0 / 12.0) - 1.0


def annual_to_daily(i_a: float, dias_uteis_ano: int = 252) -> float:
    """Converte taxa efetiva anual em taxa efetiva diária (dias úteis)."""
    return (1.0 + i_a) ** (1.0 / float(dias_uteis_ano)) - 1.0


def monthly_to_annual(i_m: float) -> float:
    """Converte taxa efetiva mensal em taxa efetiva anual."""
    return (1.0 + i_m) ** 12.0 - 1.0


def daily_to_annual(i_d: float, dias_uteis_ano: int = 252) -> float:
    """Converte taxa efetiva diária (dias úteis) em taxa efetiva anual."""
    return (1.0 + i_d) ** float(dias_uteis_ano) - 1.0


# ------------------------------
# Composição de taxas (ex.: IPCA+)
# ------------------------------
def compose_ipca_plus(ipca: float, real: float) -> float:
    """Compõe inflação (IPCA) e taxa real: (1+ipca)*(1+real) - 1."""
    return (1.0 + ipca) * (1.0 + real) - 1.0


def real_rate_from_nominal_inflation(nominal: float, ipca: float) -> float:
    """Obtém taxa real a partir de nominal e inflação: (1+nominal)/(1+ipca) - 1."""
    return (1.0 + nominal) / (1.0 + ipca) - 1.0


# ------------------------------
# Ajustes por taxas de custódia/encargos
# ------------------------------
def equivalent_periodic_fee(annual_fee: float, periods_per_year: int) -> float:
    """Equivalente por período para uma taxa anual de custódia/fee.

    Ex.: 0,2% a.a. mensal -> (1+0,002)^(1/12) - 1
    """
    return (1.0 + annual_fee) ** (1.0 / float(periods_per_year)) - 1.0


def effective_rate_with_fee(rate_effective: float, fee_effective: float) -> float:
    """Combina taxa efetiva do período com uma taxa de fee do período.

    Aplique como rendimento líquido no período: (1+rate)*(1-fee_equiv?)
    Contudo, em finanças, custódia é um encargo sobre saldo. Para simulação por período,
    costuma-se fazer: saldo_fim = saldo_ini*(1+rate) - saldo_ini*(1+rate)*fee.
    Esta função retorna uma taxa efetiva aproximada que já desconta o fee:

    (1 + i_liq) = (1 + i) * (1 - fee)  =>  i_liq = (1+i)*(1-fee) - 1
    """
    return (1.0 + rate_effective) * (1.0 - fee_effective) - 1.0


# ------------------------------
# Utilidades
# ------------------------------
def chain_rates(rates: Iterable[float]) -> float:
    """Encadeia taxas efetivas por multiplicação: Π(1+i_t) - 1.

    Útil para conferir equivalências de períodos.
    """
    acc = 1.0
    for r in rates:
        acc *= (1.0 + r)
    return acc - 1.0


__all__ = [
    "annual_to_monthly",
    "annual_to_daily",
    "monthly_to_annual",
    "daily_to_annual",
    "compose_ipca_plus",
    "real_rate_from_nominal_inflation",
    "equivalent_periodic_fee",
    "effective_rate_with_fee",
    "chain_rates",
]


