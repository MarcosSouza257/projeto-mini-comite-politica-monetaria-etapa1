from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

import pandas as pd

from rates import (
    annual_to_monthly,
    equivalent_periodic_fee,
    compose_ipca_plus,
)


@dataclass(frozen=True)
class SimulationParams:
    """Parâmetros comuns de simulação por período (mensal por padrão).

    - initial: valor inicial (VP)
    - annual_custody: taxa de custódia anual (ex.: 0,002 = 0,2% a.a.)
    - ir_rate: alíquota de IR sobre rendimentos ao final (ex.: 0,15)
    - periods_per_year: períodos por ano (12 para mensal)
    """

    initial: float
    annual_custody: float = 0.002
    ir_rate: float = 0.15
    periods_per_year: int = 12


def _simulate_timeline(
    rates: Iterable[float],
    params: SimulationParams,
    apply_custody: bool,
    ir_exempt: bool,
) -> Tuple[pd.DataFrame, float, float, float]:
    """Executa a linha do tempo mensal:

    - Acumula saldo bruto sem custódia (base do IR)
    - Aplica custódia por período (quando aplicável) sobre o saldo de fim do período
    - Ao final, calcula IR sobre (VF_bruto - VP), isentando quando necessário
    - Retorna DataFrame por período e (vf_bruto, ir_final, vf_liquido)
    """

    custody_per_period = equivalent_periodic_fee(
        params.annual_custody, params.periods_per_year
    ) if apply_custody else 0.0

    period_list = []
    saldo_sem_custodia = params.initial
    custodia_acumulada = 0.0

    for t, i_m in enumerate(rates, start=1):
        saldo_bruto_fim = saldo_sem_custodia * (1.0 + i_m)
        custodia = (saldo_bruto_fim * custody_per_period) if apply_custody else 0.0
        saldo_pos_custodia = saldo_bruto_fim - custodia

        period_list.append(
            {
                "periodo": t,
                "taxa_periodo": i_m,
                "saldo_bruto_fim": saldo_bruto_fim,
                "custodia": custodia,
                "saldo_pos_custodia": saldo_pos_custodia,
            }
        )

        # A base de IR segue a evolução sem custódia (rendimento financeiro)
        saldo_sem_custodia = saldo_bruto_fim
        custodia_acumulada += custodia

    vf_bruto = saldo_sem_custodia
    rendimento_bruto = max(0.0, vf_bruto - params.initial)
    ir_final = 0.0 if ir_exempt else params.ir_rate * rendimento_bruto
    vf_liquido = vf_bruto - ir_final - custodia_acumulada

    df = pd.DataFrame(period_list)
    return df, vf_bruto, ir_final, vf_liquido


def simulate_tesouro_prefixado(
    meses: int,
    params: SimulationParams,
    taxa_anual: float = 0.14,
) -> dict:
    """Tesouro Prefixado 2028: taxa fixa anual (padrão 14% a.a.)."""
    i_m = annual_to_monthly(taxa_anual)
    rates = [i_m] * meses
    df, vf_bruto, ir_final, vf_liq = _simulate_timeline(
        rates=rates, params=params, apply_custody=True, ir_exempt=False
    )
    return {
        "produto": "Tesouro Prefixado",
        "timeline": df,
        "vf_bruto": vf_bruto,
        "ir_final": ir_final,
        "vf_liquido": vf_liq,
    }


def simulate_tesouro_ipca_plus(
    ipca_mensal: Iterable[float],
    params: SimulationParams,
    juro_real_anual: float = 0.07,
) -> dict:
    """Tesouro IPCA+ 2028: IPCA + juro real (padrão 7% a.a.).

    Para cada mês, compõe: (1+ipca_m)*(1+i_real_m) - 1
    """
    i_real_m = annual_to_monthly(juro_real_anual)
    rates = [compose_ipca_plus(ipca, i_real_m) for ipca in ipca_mensal]
    df, vf_bruto, ir_final, vf_liq = _simulate_timeline(
        rates=rates, params=params, apply_custody=True, ir_exempt=False
    )
    return {
        "produto": "Tesouro IPCA+",
        "timeline": df,
        "vf_bruto": vf_bruto,
        "ir_final": ir_final,
        "vf_liquido": vf_liq,
    }


def simulate_tesouro_selic(
    selic_mensal: Iterable[float],
    params: SimulationParams,
) -> dict:
    """Tesouro Selic 2028: usa a Selic mensal equivalente (aproximação de diária)."""
    df, vf_bruto, ir_final, vf_liq = _simulate_timeline(
        rates=list(selic_mensal), params=params, apply_custody=True, ir_exempt=False
    )
    return {
        "produto": "Tesouro Selic",
        "timeline": df,
        "vf_bruto": vf_bruto,
        "ir_final": ir_final,
        "vf_liquido": vf_liq,
    }


def simulate_cdb_cdi(
    cdi_mensal: Iterable[float],
    params: SimulationParams,
) -> dict:
    """CDB 100% do CDI: assume CDI ≈ Selic (usar série mensal correspondente)."""
    df, vf_bruto, ir_final, vf_liq = _simulate_timeline(
        rates=list(cdi_mensal), params=params, apply_custody=True, ir_exempt=False
    )
    return {
        "produto": "CDB 100% CDI",
        "timeline": df,
        "vf_bruto": vf_bruto,
        "ir_final": ir_final,
        "vf_liquido": vf_liq,
    }


def simulate_lci(
    selic_mensal: Iterable[float],
    params: SimulationParams,
    fator: float = 0.90,
) -> dict:
    """LCI: rende fração da Selic (padrão 90%), isenta de IR. Aplica custódia."""
    rates = [fator * x for x in selic_mensal]
    df, vf_bruto, ir_final, vf_liq = _simulate_timeline(
        rates=rates, params=params, apply_custody=True, ir_exempt=True
    )
    return {
        "produto": "LCI",
        "timeline": df,
        "vf_bruto": vf_bruto,
        "ir_final": ir_final,
        "vf_liquido": vf_liq,
    }


def simulate_poupanca(
    selic_anual: Iterable[float],
    params: SimulationParams,
) -> dict:
    """Poupança: regra vigente com TR fixa de 0,17% a.m em todos os cenários.

    - Se Selic Meta > 8,5% a.a.: 0,5% a.m.
    - Caso contrário: 70% da Selic a.a. (converter para mensal)
    - Em ambos os casos, somar TR = 0,17% a.m.
    - Sem IR e sem custódia
    """
    rates = []
    tr_m = 0.0017  # 0,17% a.m.
    for s_aa in selic_anual:
        if s_aa > 0.085:
            base = 0.005  # 0,5% a.m.
        else:
            base = annual_to_monthly(0.70 * s_aa)
        rates.append(base + tr_m)

    # Poupança não tem custódia nem IR
    df, vf_bruto, ir_final, vf_liq = _simulate_timeline(
        rates=rates, params=params, apply_custody=False, ir_exempt=True
    )
    return {
        "produto": "Poupanca",
        "timeline": df,
        "vf_bruto": vf_bruto,
        "ir_final": ir_final,
        "vf_liquido": vf_liq,
    }


__all__ = [
    "SimulationParams",
    "simulate_tesouro_prefixado",
    "simulate_tesouro_ipca_plus",
    "simulate_tesouro_selic",
    "simulate_cdb_cdi",
    "simulate_lci",
    "simulate_poupanca",
]


