from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
import pandas as pd
from rates import annual_to_monthly, equivalent_periodic_fee, compose_ipca_plus
from config import TR_MENSAL_FIXA, MESES_SIMULACAO, DIAS_UTEIS_POR_ANO


@dataclass(frozen=True)
class SimulationParams:
    """Parâmetros de simulação."""
    initial: float
    annual_custody: float = 0.002
    ir_rate: float = 0.15
    periods_per_year: int = 12


def simulate_product(
    rates: Iterable[float],
    params: SimulationParams,
    produto_nome: str,
    apply_custody: bool = True,
    ir_exempt: bool = False,
) -> dict:
    """Simula um produto financeiro genérico."""
    custody_per_period = (
        equivalent_periodic_fee(params.annual_custody, params.periods_per_year)
        if apply_custody else 0.0
    )

    period_list = []
    saldo_sem_custodia = params.initial
    saldo_com_custodia = params.initial

    for i, rate in enumerate(rates, 1):
        # Aplica rendimento
        saldo_sem_custodia *= (1.0 + rate)
        saldo_com_custodia *= (1.0 + rate)
        
        # Aplica custódia
        custodia_periodo = saldo_com_custodia * custody_per_period if apply_custody else 0.0
        saldo_com_custodia -= custodia_periodo

        period_list.append({
            "periodo": i,
            "taxa": rate,
            "saldo_bruto": saldo_sem_custodia,
            "custodia": custodia_periodo,
            "saldo_pos_custodia": saldo_com_custodia,
        })

    df = pd.DataFrame(period_list)
    vf_bruto = saldo_sem_custodia
    
    # Calcula IR
    if ir_exempt:
        ir_final = 0.0
    else:
        ganho = max(0.0, vf_bruto - params.initial)
        ir_final = ganho * params.ir_rate
    
    vf_liquido = saldo_com_custodia - ir_final

    return {
        "produto": produto_nome,
        "timeline": df,
        "vf_bruto": vf_bruto,
        "ir_final": ir_final,
        "vf_liquido": vf_liquido,
    }


def simulate_tesouro_prefixado(meses: int, params: SimulationParams, taxa_anual: float = 0.14) -> dict:
    """Tesouro Prefixado: taxa fixa de 14% a.a."""
    if params.periods_per_year == 252:  # Simulação diária
        rate = (1.0 + taxa_anual) ** (1.0 / 252.0) - 1.0
    else:  # Simulação mensal
        rate = annual_to_monthly(taxa_anual)
    
    rates = [rate] * meses
    return simulate_product(rates, params, "Tesouro Prefixado", apply_custody=True, ir_exempt=False)


def simulate_tesouro_ipca_plus(ipca_mensal: Iterable[float], params: SimulationParams, juro_real_anual: float = 0.07) -> dict:
    """Tesouro IPCA+: IPCA + 7% a.a. real."""
    i_real_m = annual_to_monthly(juro_real_anual)
    rates = []
    
    for ipca_anual in ipca_mensal:
        ipca_m = annual_to_monthly(ipca_anual)
        taxa_composta = compose_ipca_plus(ipca_m, i_real_m)
        rates.append(taxa_composta)
    
    return simulate_product(rates, params, "Tesouro IPCA+", apply_custody=True, ir_exempt=False)


def simulate_tesouro_selic(selic_mensal: Iterable[float], params: SimulationParams) -> dict:
    """Tesouro Selic: acompanha a Selic."""
    return simulate_product(list(selic_mensal), params, "Tesouro Selic", apply_custody=True, ir_exempt=False)


def simulate_cdb_cdi(cdi_mensal: Iterable[float], params: SimulationParams) -> dict:
    """CDB 100% CDI: assume CDI ≈ Selic."""
    return simulate_product(list(cdi_mensal), params, "CDB 100% CDI", apply_custody=True, ir_exempt=False)


def simulate_lci(selic_mensal: Iterable[float], params: SimulationParams, fator: float = 0.90) -> dict:
    """LCI: 90% da Selic, isenta de IR."""
    rates = [fator * x for x in selic_mensal]
    return simulate_product(rates, params, "LCI", apply_custody=True, ir_exempt=True)

def get_poupanca_base_rate(selic_aa: float) -> float:
    """Calcula taxa base da poupança (sem TR) em termos mensais."""
    if selic_aa > 0.085:  # Selic > 8,5% a.a.
        return 0.005  # 0,5% a.m.
    return annual_to_monthly(0.70 * selic_aa)


def simulate_poupanca(selic_anual: Iterable[float], params: SimulationParams) -> dict:
    """Simula a poupança conforme regra vigente:
    - Selic > 8,5% a.a. → 0,5% a.m. + TR
    - Selic ≤ 8,5% a.a. → 70% da Selic a.a. (convertido a.m.) + TR
    Obs: Capitalização é mensal (data de aniversário).
    """
    tr_m = TR_MENSAL_FIXA
    selic_list = list(selic_anual)
    rates = []

    if params.periods_per_year == DIAS_UTEIS_POR_ANO: 
        dias_por_mes = 21
        for mes in range(len(selic_list) // dias_por_mes):
            idx_dia = mes * dias_por_mes
            s_aa = selic_list[idx_dia]

            # Taxa mensal da poupança
            taxa_mensal = get_poupanca_base_rate(s_aa) + tr_m

            # Durante o mês não há rendimento (dias sem aniversário)
            rates.extend([0.0] * (dias_por_mes - 1))

            # No aniversário (último dia do mês), aplica a taxa mensal
            rates.append(taxa_mensal)

        # Ajuste se houver sobra de dias no final
        if len(rates) < len(selic_list):
            rates.extend([0.0] * (len(selic_list) - len(rates)))
        rates = rates[:len(selic_list)]

    else:  # Simulação mensal (36 meses, por ex.)
        for s_aa in selic_list:
            rates.append(get_poupanca_base_rate(s_aa) + tr_m)
    
    return simulate_product(rates, params, "Poupanca", apply_custody=False, ir_exempt=True)
