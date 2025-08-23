from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd
from config import CENARIOS, CenarioEconomico, ANOS_SIMULACAO, MESES_SIMULACAO, DIAS_UTEIS_SIMULACAO, DIAS_UTEIS_POR_ANO


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
    selic_by_year: List[float]  # tamanho ANOS_SIMULACAO
    ipca_by_year: List[float]   # tamanho ANOS_SIMULACAO
    start_year: int = 2025


def _expand_annual_sequence_to_months(
    annual_sequence: List[float], months: int = MESES_SIMULACAO
) -> List[float]:
    """Repete cada taxa anual para seus 12 meses correspondentes.

    annual_sequence deve ter tamanho ANOS_SIMULACAO.
    """
    if len(annual_sequence) != ANOS_SIMULACAO:
        raise ValueError(f"annual_sequence deve conter exatamente {ANOS_SIMULACAO} taxas anuais")
    per_year_months = months // ANOS_SIMULACAO
    expanded: List[float] = []
    for annual in annual_sequence:
        expanded.extend([annual] * per_year_months)
    # Se months não for múltiplo de ANOS_SIMULACAO*12, ajusta/trunca
    return expanded[:months]


def build_scenario_dataframe(
    definition: ScenarioDefinition,
    months: int = MESES_SIMULACAO,
    business_days_per_year: int = DIAS_UTEIS_POR_ANO,
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
        # Distribui os meses pelos anos de simulação
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
    business_days_per_year: int = DIAS_UTEIS_POR_ANO,
) -> pd.DataFrame:
    """Constroi um DataFrame diário para o cenário informado.

    Colunas:
    - scenario: nome do cenário
    - day_index: 1..DIAS_UTEIS_SIMULACAO (dias úteis)
    - year: anos de simulação (repetido a cada business_days_per_year dias úteis)
    - selic_aa, ipca_aa: taxas anuais daquele dia (valores anuais expandidos)
    - selic_d, ipca_d: taxas efetivas diárias (dias úteis)
    """
    total_days = DIAS_UTEIS_SIMULACAO
    
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
        # Distribui os dias pelos anos de simulação
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
# Funções para construir cenários a partir da configuração
# ------------------------------

def build_scenario_from_config(cenario_key: str, include_daily_columns: bool = False) -> pd.DataFrame:
    """Constrói um cenário a partir da configuração centralizada."""
    if cenario_key not in CENARIOS:
        raise ValueError(f"Cenário '{cenario_key}' não encontrado. Disponíveis: {list(CENARIOS.keys())}")
    
    cenario = CENARIOS[cenario_key]
    definition = ScenarioDefinition(
        name=cenario.nome,
        selic_by_year=cenario.selic_por_ano,
        ipca_by_year=cenario.ipca_por_ano,
    )
    return build_scenario_dataframe(definition, include_daily_columns=include_daily_columns)


def build_scenario_daily_from_config(cenario_key: str) -> pd.DataFrame:
    """Constrói um cenário diário a partir da configuração centralizada."""
    if cenario_key not in CENARIOS:
        raise ValueError(f"Cenário '{cenario_key}' não encontrado. Disponíveis: {list(CENARIOS.keys())}")
    
    cenario = CENARIOS[cenario_key]
    definition = ScenarioDefinition(
        name=cenario.nome,
        selic_by_year=cenario.selic_por_ano,
        ipca_by_year=cenario.ipca_por_ano,
    )
    return build_scenario_dataframe_daily(definition)


# ------------------------------
# Cenários pré-definidos (mantidos para compatibilidade)
# ------------------------------
def scenario_manutencao(include_daily_columns: bool = False) -> pd.DataFrame:
    """Cenário 1 (Manutenção): usa configuração centralizada."""
    return build_scenario_from_config("manutencao", include_daily_columns)


def scenario_manutencao_daily() -> pd.DataFrame:
    """Cenário 1 (Manutenção): versão diária usando configuração centralizada."""
    return build_scenario_daily_from_config("manutencao")


def scenario_aperto(include_daily_columns: bool = False) -> pd.DataFrame:
    """Cenário 2 (Aperto Monetário): usa configuração centralizada."""
    return build_scenario_from_config("aperto", include_daily_columns)


def scenario_aperto_daily() -> pd.DataFrame:
    """Cenário 2 (Aperto): versão diária usando configuração centralizada."""
    return build_scenario_daily_from_config("aperto")


def scenario_afrouxamento(include_daily_columns: bool = False) -> pd.DataFrame:
    """Cenário 3 (Afrouxamento Monetário): usa configuração centralizada."""
    return build_scenario_from_config("afrouxamento", include_daily_columns)


def scenario_afrouxamento_daily() -> pd.DataFrame:
    """Cenário 3 (Afrouxamento): versão diária usando configuração centralizada."""
    return build_scenario_daily_from_config("afrouxamento")


def get_all_scenarios(include_daily_columns: bool = False) -> Dict[str, pd.DataFrame]:
    """Retorna todos os cenários configurados como dict: nome -> DataFrame."""
    scenarios = {}
    for key in CENARIOS.keys():
        df = build_scenario_from_config(key, include_daily_columns)
        scenarios[df["scenario"].iloc[0]] = df
    return scenarios


def get_all_scenarios_daily() -> Dict[str, pd.DataFrame]:
    """Retorna todos os cenários configurados em versão diária."""
    scenarios = {}
    for key in CENARIOS.keys():
        df = build_scenario_daily_from_config(key)
        scenarios[df["scenario"].iloc[0]] = df
    return scenarios


def list_available_scenarios() -> Dict[str, str]:
    """Lista todos os cenários disponíveis com suas descrições."""
    return {key: cenario.descricao for key, cenario in CENARIOS.items()}


__all__ = [
    "ScenarioDefinition",
    "annual_to_monthly",
    "annual_to_daily",
    "build_scenario_dataframe",
    "build_scenario_dataframe_daily",
    # Funções que usam configuração centralizada
    "build_scenario_from_config",
    "build_scenario_daily_from_config",
    "get_all_scenarios",
    "get_all_scenarios_daily",
    "list_available_scenarios",
    # Funções de compatibilidade (cenários específicos)
    "scenario_manutencao",
    "scenario_manutencao_daily",
    "scenario_aperto",
    "scenario_aperto_daily",
    "scenario_afrouxamento",
    "scenario_afrouxamento_daily",
]


