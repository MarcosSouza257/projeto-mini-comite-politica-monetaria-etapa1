from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
import pandas as pd
from rates import annual_to_monthly, annual_to_daily, monthly_to_annual, daily_to_annual, equivalent_periodic_fee, compose_ipca_plus
from config import TR_MENSAL_FIXA, DIAS_UTEIS_POR_ANO, SPREAD_CDI_SELIC


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
    # Determina função de conversão baseada na frequência da simulação
    convert_rate = annual_to_daily if params.periods_per_year == DIAS_UTEIS_POR_ANO else annual_to_monthly
    
    # Converte taxa anual para o período da simulação e replica para todos os períodos
    rate = convert_rate(taxa_anual)
    rates = [rate] * meses
    
    return simulate_product(rates, params, "Tesouro Prefixado", apply_custody=True, ir_exempt=False)


def simulate_tesouro_ipca_plus(ipca_mensal: Iterable[float], params: SimulationParams, juro_real_anual: float = 0.07) -> dict:
    """Tesouro IPCA+: IPCA + 7% a.a. real."""
    # Determina função de conversão baseada na frequência da simulação
    if params.periods_per_year == DIAS_UTEIS_POR_ANO:
        convert_rate = annual_to_daily
    else:
        convert_rate = annual_to_monthly
    
    # Converte juro real anual para o período da simulação
    i_real_periodo = convert_rate(juro_real_anual)
    
    # Calcula taxas compostas para cada período
    rates = [
        compose_ipca_plus(convert_rate(ipca_anual), i_real_periodo) 
        for ipca_anual in ipca_mensal
    ]
    
    return simulate_product(rates, params, "Tesouro IPCA+", apply_custody=True, ir_exempt=False)


def simulate_tesouro_selic(selic_mensal: Iterable[float], params: SimulationParams) -> dict:
    """Tesouro Selic: acompanha a Selic."""
    return simulate_product(list(selic_mensal), params, "Tesouro Selic", apply_custody=True, ir_exempt=False)


def calculate_cdi_from_selic(selic_rates: Iterable[float], params: SimulationParams) -> list[float]:
    """Calcula taxas CDI baseadas na Selic com spread realista.
    
    CDI geralmente fica 0,1 p.p. abaixo da Selic (conforme B3).
    Exemplo: Se Selic = 15% a.a. → CDI ≈ 14,9% a.a.
    """
    # Determina funções de conversão baseada na frequência da simulação
    if params.periods_per_year == DIAS_UTEIS_POR_ANO:
        to_annual, from_annual = daily_to_annual, annual_to_daily
    else:
        to_annual, from_annual = monthly_to_annual, annual_to_monthly
    
    # Calcula CDI para cada período
    cdi_rates = []
    for selic_periodo in selic_rates:
        # Converte para anual, aplica spread, converte de volta
        selic_anual = to_annual(selic_periodo)
        cdi_anual = selic_anual + SPREAD_CDI_SELIC  # -0,1 p.p.
        cdi_periodo = from_annual(cdi_anual)
        cdi_rates.append(cdi_periodo)
    
    return cdi_rates


def simulate_cdb_cdi(selic_rates: Iterable[float], params: SimulationParams) -> dict:
    """CDB 100% CDI: CDI fica ~0,1 p.p. abaixo da Selic (conforme B3)."""
    cdi_rates = calculate_cdi_from_selic(selic_rates, params)
    return simulate_product(cdi_rates, params, "CDB 100% CDI", apply_custody=True, ir_exempt=False)


def simulate_lci(selic_mensal: Iterable[float], params: SimulationParams, fator: float = 0.90) -> dict:
    """LCI: 90% da Selic, isenta de IR.
    
    Implementa corretamente: Se Selic = 15% a.a., então LCI = 13,5% a.a.
    Converte a taxa anual equivalente e depois para o período da simulação.
    """
    # Determina funções de conversão baseada na frequência da simulação
    if params.periods_per_year == DIAS_UTEIS_POR_ANO:
        to_annual, from_annual = daily_to_annual, annual_to_daily
    else:
        to_annual, from_annual = monthly_to_annual, annual_to_monthly
    
    # Calcula taxas LCI para cada período
    rates = [
        from_annual(fator * to_annual(selic_periodo))
        for selic_periodo in selic_mensal
    ]
    
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
    selic_list = list(selic_anual)
    
    if params.periods_per_year == DIAS_UTEIS_POR_ANO:
        # Simulação diária: capitalização apenas no aniversário (último dia do mês)
        rates = []
        dias_por_mes = 21
        
        for mes in range(len(selic_list) // dias_por_mes):
            idx_dia = mes * dias_por_mes
            s_aa = selic_list[idx_dia]
            
            # Taxa mensal da poupança (base + TR)
            taxa_mensal = get_poupanca_base_rate(s_aa) + TR_MENSAL_FIXA
            
            # 20 dias sem rendimento + 1 dia com taxa mensal
            rates.extend([0.0] * (dias_por_mes - 1) + [taxa_mensal])
        
        # Ajusta para o tamanho exato da lista
        rates = (rates + [0.0] * len(selic_list))[:len(selic_list)]
    else:
        # Simulação mensal: aplica taxa mensal diretamente
        rates = [get_poupanca_base_rate(s_aa) + TR_MENSAL_FIXA for s_aa in selic_list]
    
    return simulate_product(rates, params, "Poupanca", apply_custody=False, ir_exempt=True)
