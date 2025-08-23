from __future__ import annotations

from typing import Dict

import pandas as pd
from config import CAPITAL_INICIAL, DIAS_UTEIS_POR_ANO

from scenarios import (
    scenario_manutencao,
    scenario_aperto,
    scenario_afrouxamento,
    scenario_manutencao_daily,
    scenario_aperto_daily,
    scenario_afrouxamento_daily,
    get_all_scenarios_daily,
)
from products import (
    SimulationParams,
    simulate_tesouro_prefixado,
    simulate_tesouro_ipca_plus,
    simulate_tesouro_selic,
    simulate_cdb_cdi,
    simulate_lci,
    simulate_poupanca,
)


def _simulate_for_scenario_daily(df: pd.DataFrame, params: SimulationParams) -> Dict:
    """Executa todos os produtos para um DataFrame de cenário diário (756 linhas diárias)."""
    # Séries necessárias (agora diárias)
    selic_d = df["selic_d"].tolist()
    ipca_d = df["ipca_d"].tolist()
    ipca_aa = df["ipca_aa"].tolist()  # IPCA anual para Tesouro IPCA+
    selic_aa = df["selic_aa"].tolist()

    results = []

    # Simula todos os produtos (agora com 756 dias úteis)
    r_prefix = simulate_tesouro_prefixado(meses=len(df), params=params)  # taxa fixa 14% a.a.
    r_ipca = simulate_tesouro_ipca_plus(ipca_mensal=ipca_aa, params=params)  # usa IPCA anual
    r_selic = simulate_tesouro_selic(selic_mensal=selic_d, params=params)   # usa Selic diário
    r_cdb = simulate_cdb_cdi(selic_rates=selic_d, params=params)            # CDI ≈ Selic - 0,1 p.p.
    r_lci = simulate_lci(selic_mensal=selic_d, params=params)               # usa Selic diário
    r_poup = simulate_poupanca(selic_anual=selic_aa, params=params)

    # Cria resumo
    summary_data = [
        {"produto": r_prefix["produto"], "vf_bruto": r_prefix["vf_bruto"], 
         "ir_final": r_prefix["ir_final"], "vf_liquido": r_prefix["vf_liquido"]},
        {"produto": r_ipca["produto"], "vf_bruto": r_ipca["vf_bruto"], 
         "ir_final": r_ipca["ir_final"], "vf_liquido": r_ipca["vf_liquido"]},
        {"produto": r_selic["produto"], "vf_bruto": r_selic["vf_bruto"], 
         "ir_final": r_selic["ir_final"], "vf_liquido": r_selic["vf_liquido"]},
        {"produto": r_cdb["produto"], "vf_bruto": r_cdb["vf_bruto"], 
         "ir_final": r_cdb["ir_final"], "vf_liquido": r_cdb["vf_liquido"]},
        {"produto": r_lci["produto"], "vf_bruto": r_lci["vf_bruto"], 
         "ir_final": r_lci["ir_final"], "vf_liquido": r_lci["vf_liquido"]},
        {"produto": r_poup["produto"], "vf_bruto": r_poup["vf_bruto"], 
         "ir_final": r_poup["ir_final"], "vf_liquido": r_poup["vf_liquido"]},
    ]
    
    summary_df = pd.DataFrame(summary_data).sort_values("vf_liquido", ascending=False).reset_index(drop=True)
    
    # Organiza timelines
    timelines = {
        "Tesouro_Prefixado": r_prefix["timeline"],
        "Tesouro_IPCA_Plus": r_ipca["timeline"],
        "Tesouro_Selic": r_selic["timeline"],
        "CDB_100_CDI": r_cdb["timeline"],
        "LCI": r_lci["timeline"],
        "Poupanca": r_poup["timeline"],
    }
    
    return {
        "summary": summary_df,
        "timelines": timelines
    }


def _simulate_for_scenario(df: pd.DataFrame, params: SimulationParams) -> pd.DataFrame:
    """Executa todos os produtos para um DataFrame de cenário mensal (36 linhas mensais)."""
    # Séries necessárias
    selic_m = df["selic_m"].tolist()
    ipca_m = df["ipca_m"].tolist()
    selic_aa = df["selic_aa"].tolist()

    results = []

    r_prefix = simulate_tesouro_prefixado(meses=len(df), params=params)
    results.append({
        "produto": r_prefix["produto"],
        "vf_bruto": r_prefix["vf_bruto"],
        "ir_final": r_prefix["ir_final"],
        "vf_liquido": r_prefix["vf_liquido"],
    })

    r_ipca = simulate_tesouro_ipca_plus(ipca_mensal=ipca_m, params=params)
    results.append({
        "produto": r_ipca["produto"],
        "vf_bruto": r_ipca["vf_bruto"],
        "ir_final": r_ipca["ir_final"],
        "vf_liquido": r_ipca["vf_liquido"],
    })

    r_selic = simulate_tesouro_selic(selic_mensal=selic_m, params=params)
    results.append({
        "produto": r_selic["produto"],
        "vf_bruto": r_selic["vf_bruto"],
        "ir_final": r_selic["ir_final"],
        "vf_liquido": r_selic["vf_liquido"],
    })

    r_cdb = simulate_cdb_cdi(selic_rates=selic_m, params=params)
    results.append({
        "produto": r_cdb["produto"],
        "vf_bruto": r_cdb["vf_bruto"],
        "ir_final": r_cdb["ir_final"],
        "vf_liquido": r_cdb["vf_liquido"],
    })

    r_lci = simulate_lci(selic_mensal=selic_m, params=params)
    results.append({
        "produto": r_lci["produto"],
        "vf_bruto": r_lci["vf_bruto"],
        "ir_final": r_lci["ir_final"],
        "vf_liquido": r_lci["vf_liquido"],
    })

    r_poup = simulate_poupanca(selic_anual=selic_aa, params=params)
    results.append({
        "produto": r_poup["produto"],
        "vf_bruto": r_poup["vf_bruto"],
        "ir_final": r_poup["ir_final"],
        "vf_liquido": r_poup["vf_liquido"],
    })

    df_summary = pd.DataFrame(results).sort_values("vf_liquido", ascending=False).reset_index(drop=True)
    return df_summary


def run_all(initial_value: float = CAPITAL_INICIAL) -> Dict[str, pd.DataFrame]:
    """Roda todos os cenários com parâmetros padrão e retorna resumos por cenário."""
    params = SimulationParams(initial=initial_value, annual_custody=0.002, periods_per_year=12)

    scen1 = scenario_manutencao()
    scen2 = scenario_aperto()
    scen3 = scenario_afrouxamento()

    return {
        scen1["scenario"].iloc[0]: _simulate_for_scenario(scen1, params),
        scen2["scenario"].iloc[0]: _simulate_for_scenario(scen2, params),
        scen3["scenario"].iloc[0]: _simulate_for_scenario(scen3, params),
    }

def run_all_with_timelines(initial_value: float = CAPITAL_INICIAL) -> Dict[str, Dict]:
    """Roda todos os cenários configurados e retorna resumos + timelines completas por cenário."""
    params = SimulationParams(initial=initial_value, annual_custody=0.002, periods_per_year=DIAS_UTEIS_POR_ANO)

    # Usa todos os cenários configurados dinamicamente
    all_scenarios = get_all_scenarios_daily()
    
    results = {}
    for scenario_name, scenario_df in all_scenarios.items():
        results[scenario_name] = _simulate_for_scenario_daily(scenario_df, params)
    
    return results


def main() -> None:
    res = run_all()
    for scen_name, df in res.items():
        print(f"\n=== {scen_name} ===")
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
