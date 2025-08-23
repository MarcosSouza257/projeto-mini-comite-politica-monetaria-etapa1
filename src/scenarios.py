
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import pandas as pd
from config import (
    ANOS_SIMULACAO, MESES_SIMULACAO, DIAS_UTEIS_SIMULACAO, DIAS_UTEIS_POR_ANO,
    CENARIOS_CONFIG,
)


@dataclass(frozen=True)
class CenarioEconomico:
    """Define um cenário econômico com trajetórias de Selic e IPCA."""
    nome: str
    descricao: str
    selic_por_ano: List[float]
    ipca_por_ano: List[float]


def annual_to_monthly(annual_rate: float) -> float:
    """Converte taxa anual para mensal."""
    return (1.0 + annual_rate) ** (1.0 / 12.0) - 1.0


def annual_to_daily(annual_rate: float, days_per_year: int = DIAS_UTEIS_POR_ANO) -> float:
    """Converte taxa anual para diária."""
    return (1.0 + annual_rate) ** (1.0 / days_per_year) - 1.0


def build_scenario_dataframe(cenario: CenarioEconomico, granularity: str = "monthly") -> pd.DataFrame:
    """Constrói DataFrame para o cenário com granularidade mensal ou diária."""
    if granularity == "monthly":
        total_periods = MESES_SIMULACAO
        periods_per_year = 12
        index_name = "month_index"
        rate_suffix = "m"
        convert_rate = annual_to_monthly
    elif granularity == "daily":
        total_periods = DIAS_UTEIS_SIMULACAO
        periods_per_year = DIAS_UTEIS_POR_ANO
        index_name = "day_index"
        rate_suffix = "d"
        convert_rate = annual_to_daily
    else:
        raise ValueError("Granularidade deve ser 'monthly' ou 'daily'.")

    # Expande taxas anuais para períodos
    selic_aa = []
    ipca_aa = []
    years = []
    
    for year_idx in range(ANOS_SIMULACAO):
        selic_aa.extend([cenario.selic_por_ano[year_idx]] * periods_per_year)
        ipca_aa.extend([cenario.ipca_por_ano[year_idx]] * periods_per_year)
        years.extend([2025 + year_idx] * periods_per_year)

    # Trunca para o total exato de períodos
    selic_aa = selic_aa[:total_periods]
    ipca_aa = ipca_aa[:total_periods]
    years = years[:total_periods]

    # Converte para taxas periódicas
    selic_p = [convert_rate(x) for x in selic_aa]
    ipca_p = [convert_rate(x) for x in ipca_aa]

    return pd.DataFrame({
        "scenario": [cenario.nome] * total_periods,
        index_name: list(range(1, total_periods + 1)),
        "year": years,
        "selic_aa": selic_aa,
        "ipca_aa": ipca_aa,
        f"selic_{rate_suffix}": selic_p,
        f"ipca_{rate_suffix}": ipca_p,
    })


# Criação automática dos cenários
CENARIOS = {
    key: CenarioEconomico(
        nome=config["nome"],
        descricao=config["descricao"],
        selic_por_ano=config["selic_por_ano"],
        ipca_por_ano=config["ipca_por_ano"],
    )
    for key, config in CENARIOS_CONFIG.items()
}


def get_scenario(key: str, granularity: str = "monthly") -> pd.DataFrame:
    """Retorna DataFrame do cenário especificado."""
    if key not in CENARIOS:
        raise ValueError(f"Cenário '{key}' não encontrado. Disponíveis: {list(CENARIOS.keys())}")
    return build_scenario_dataframe(CENARIOS[key], granularity)


def get_all_scenarios_daily() -> Dict[str, pd.DataFrame]:
    """Retorna todos os cenários em versão diária."""
    return {
        cenario.nome: build_scenario_dataframe(cenario, "daily")
        for cenario in CENARIOS.values()
    }


# Funções de compatibilidade (para não quebrar código existente)
def scenario_manutencao(include_daily_columns: bool = False) -> pd.DataFrame:
    df = get_scenario("Manutencao", "monthly")
    if include_daily_columns:
        df["selic_d"] = [annual_to_daily(x) for x in df["selic_aa"]]
        df["ipca_d"] = [annual_to_daily(x) for x in df["ipca_aa"]]
    return df

def scenario_aperto(include_daily_columns: bool = False) -> pd.DataFrame:
    df = get_scenario("Aperto", "monthly")
    if include_daily_columns:
        df["selic_d"] = [annual_to_daily(x) for x in df["selic_aa"]]
        df["ipca_d"] = [annual_to_daily(x) for x in df["ipca_aa"]]
    return df

def scenario_afrouxamento(include_daily_columns: bool = False) -> pd.DataFrame:
    df = get_scenario("Afrouxamento", "monthly")
    if include_daily_columns:
        df["selic_d"] = [annual_to_daily(x) for x in df["selic_aa"]]
        df["ipca_d"] = [annual_to_daily(x) for x in df["ipca_aa"]]
    return df

def scenario_manutencao_daily() -> pd.DataFrame:
    return get_scenario("Manutencao", "daily")

def scenario_aperto_daily() -> pd.DataFrame:
    return get_scenario("Aperto", "daily")

def scenario_afrouxamento_daily() -> pd.DataFrame:
    return get_scenario("Afrouxamento", "daily")
