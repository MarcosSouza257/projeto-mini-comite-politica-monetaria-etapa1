from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd


# ------------------------------
# Auxiliares: conversão de taxas
# ------------------------------
def annual_to_monthly(annual_rate: float) -> float:
    """Converte taxa efetiva anual em taxa efetiva mensal.

    Exemplo: 15% a.a. -> (1+0,15)^(1/12) - 1
    """
    return (1.0 + annual_rate) ** (1.0 / 12.0) - 1.0


def annual_to_daily(annual_rate: float, business_days_per_year: int = 252) -> float:
    """Converte taxa efetiva anual em taxa efetiva diária (dias úteis)."""
    return (1.0 + annual_rate) ** (1.0 / float(business_days_per_year)) - 1.0


@dataclass(frozen=True)
class ScenarioDefinition:
    name: str
    selic_by_year: List[float]  # tamanho 3: anos Y0, Y1, Y2
    ipca_by_year: List[float]   # tamanho 3: anos Y0, Y1, Y2
    start_year: int = 2025


def _expand_annual_sequence_to_months(
    annual_sequence: List[float], months: int = 36
) -> List[float]:
    """Repete cada taxa anual para seus 12 meses correspondentes, por 3 anos.

    annual_sequence deve ter tamanho 3.
    """
    if len(annual_sequence) != 3:
        raise ValueError("annual_sequence deve conter exatamente 3 taxas anuais (anos 1..3)")
    per_year_months = months // 3
    expanded: List[float] = []
    for annual in annual_sequence:
        expanded.extend([annual] * per_year_months)
    # Se months não for múltiplo de 3*12, ajusta/trunca (não esperado para 36)
    return expanded[:months]


def build_scenario_dataframe(
    definition: ScenarioDefinition,
    months: int = 36,
    business_days_per_year: int = 252,
    include_daily_columns: bool = False,
) -> pd.DataFrame:
    """Constroi um DataFrame mensal para o cenário informado.

    Colunas:
    - scenario: nome do cenário
    - month_index: 1..months
    - year: start_year, start_year+1, start_year+2 (repetido a cada 12 meses)
    - selic_aa, ipca_aa: taxas anuais daquele mês (valores anuais expandidos)
    - selic_m, ipca_m: taxas efetivas mensais
    - [opcional] selic_d, ipca_d: taxas efetivas diárias (dias úteis)
    """
    selic_aa_monthly = _expand_annual_sequence_to_months(definition.selic_by_year, months=months)
    ipca_aa_monthly = _expand_annual_sequence_to_months(definition.ipca_by_year, months=months)

    # Índice mensal e mapeamento de ano
    month_index = list(range(1, months + 1))
    years: List[int] = []
    for i in month_index:
        # Meses 1..12 -> Y0, 13..24 -> Y1, 25..36 -> Y2
        year_offset = (i - 1) // 12
        years.append(definition.start_year + year_offset)

    # Conversões para taxa mensal
    selic_m = [annual_to_monthly(x) for x in selic_aa_monthly]
    ipca_m = [annual_to_monthly(x) for x in ipca_aa_monthly]

    data = {
        "scenario": [definition.name] * months,
        "month_index": month_index,
        "year": years,
        "selic_aa": selic_aa_monthly,
        "ipca_aa": ipca_aa_monthly,
        "selic_m": selic_m,
        "ipca_m": ipca_m,
    }

    if include_daily_columns:
        data["selic_d"] = [annual_to_daily(x, business_days_per_year) for x in selic_aa_monthly]
        data["ipca_d"] = [annual_to_daily(x, business_days_per_year) for x in ipca_aa_monthly]

    return pd.DataFrame(data)


def build_scenario_dataframe_daily(
    definition: ScenarioDefinition,
    business_days_per_year: int = 252,
) -> pd.DataFrame:
    """Constroi um DataFrame diário para o cenário informado (3 anos = 756 dias úteis).

    Colunas:
    - scenario: nome do cenário
    - day_index: 1..756 (dias úteis)
    - year: start_year, start_year+1, start_year+2 (repetido a cada 252 dias úteis)
    - selic_aa, ipca_aa: taxas anuais daquele dia (valores anuais expandidos)
    - selic_d, ipca_d: taxas efetivas diárias (dias úteis)
    """
    total_days = 3 * business_days_per_year  # 756 dias úteis
    
    # Expande taxas anuais para dias úteis
    selic_aa_daily = []
    ipca_aa_daily = []
    for year_idx, (selic_aa, ipca_aa) in enumerate(zip(definition.selic_by_year, definition.ipca_by_year)):
        selic_aa_daily.extend([selic_aa] * business_days_per_year)
        ipca_aa_daily.extend([ipca_aa] * business_days_per_year)
    
    # Day index and year mapping
    day_index = list(range(1, total_days + 1))
    years = []
    for i in day_index:
        # Days 1..252 -> Y0, 253..504 -> Y1, 505..756 -> Y2
        year_offset = (i - 1) // business_days_per_year
        years.append(definition.start_year + year_offset)

    # Daily conversions
    selic_d = [annual_to_daily(x, business_days_per_year) for x in selic_aa_daily]
    ipca_d = [annual_to_daily(x, business_days_per_year) for x in ipca_aa_daily]

    data = {
        "scenario": [definition.name] * total_days,
        "day_index": day_index,
        "year": years,
        "selic_aa": selic_aa_daily,
        "ipca_aa": ipca_aa_daily,
        "selic_d": selic_d,
        "ipca_d": ipca_d,
    }

    return pd.DataFrame(data)


# ------------------------------
# Cenários pré-definidos
# ------------------------------
def scenario_manutencao(include_daily_columns: bool = False) -> pd.DataFrame:
    """Cenário 1 (Manutenção): Selic 15% a.a. nos 3 anos; IPCA 4,5% a.a. nos 3 anos."""
    definition = ScenarioDefinition(
        name="Cenario 1 - Manutencao",
        selic_by_year=[0.15, 0.15, 0.15],
        ipca_by_year=[0.045, 0.045, 0.045],
    )
    return build_scenario_dataframe(definition, include_daily_columns=include_daily_columns)


def scenario_manutencao_daily() -> pd.DataFrame:
    """Cenário 1 (Manutenção): versão diária com 756 dias úteis."""
    definition = ScenarioDefinition(
        name="Cenario 1 - Manutencao",
        selic_by_year=[0.15, 0.15, 0.15],
        ipca_by_year=[0.045, 0.045, 0.045],
    )
    return build_scenario_dataframe_daily(definition)


def scenario_aperto(include_daily_columns: bool = False) -> pd.DataFrame:
    """Cenário 2 (Aperto Monetário):
    - Selic: 15% (2025), 16,5% (2026), 17% (2027)
    - IPCA: 4,5% (2025), 5,0% (2026), 5,5% (2027)
    """
    definition = ScenarioDefinition(
        name="Cenario 2 - Aperto",
        selic_by_year=[0.15, 0.165, 0.17],
        ipca_by_year=[0.045, 0.05, 0.055],
    )
    return build_scenario_dataframe(definition, include_daily_columns=include_daily_columns)


def scenario_aperto_daily() -> pd.DataFrame:
    """Cenário 2 (Aperto): versão diária com 756 dias úteis."""
    definition = ScenarioDefinition(
        name="Cenario 2 - Aperto",
        selic_by_year=[0.15, 0.165, 0.17],
        ipca_by_year=[0.045, 0.05, 0.055],
    )
    return build_scenario_dataframe_daily(definition)


def scenario_afrouxamento(include_daily_columns: bool = False) -> pd.DataFrame:
    """Cenário 3 (Afrouxamento Monetário):
    - Selic: 15% (2025), 13% (2026), 11% (2027)
    - IPCA: 4% a.a. nos 3 anos
    """
    definition = ScenarioDefinition(
        name="Cenario 3 - Afrouxamento",
        selic_by_year=[0.15, 0.13, 0.11],
        ipca_by_year=[0.04, 0.04, 0.04],
    )
    return build_scenario_dataframe(definition, include_daily_columns=include_daily_columns)


def scenario_afrouxamento_daily() -> pd.DataFrame:
    """Cenário 3 (Afrouxamento): versão diária com 756 dias úteis."""
    definition = ScenarioDefinition(
        name="Cenario 3 - Afrouxamento",
        selic_by_year=[0.15, 0.13, 0.11],
        ipca_by_year=[0.04, 0.04, 0.04],
    )
    return build_scenario_dataframe_daily(definition)


def get_all_scenarios(include_daily_columns: bool = False) -> Dict[str, pd.DataFrame]:
    """Retorna todos os cenários pré-definidos como dict: nome -> DataFrame."""
    dfs = [
        scenario_manutencao(include_daily_columns=include_daily_columns),
        scenario_aperto(include_daily_columns=include_daily_columns),
        scenario_afrouxamento(include_daily_columns=include_daily_columns),
    ]
    return {df["scenario"].iloc[0]: df for df in dfs}


__all__ = [
    "ScenarioDefinition",
    "annual_to_monthly",
    "annual_to_daily",
    "build_scenario_dataframe",
    "build_scenario_dataframe_daily",
    "scenario_manutencao",
    "scenario_manutencao_daily",
    "scenario_aperto",
    "scenario_aperto_daily",
    "scenario_afrouxamento",
    "scenario_afrouxamento_daily",
    "get_all_scenarios",
]


