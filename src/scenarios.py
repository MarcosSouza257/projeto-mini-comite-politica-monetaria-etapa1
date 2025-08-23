"""
Versão simplificada do módulo scenarios.py
Consolida a lógica de criação de cenários econômicos.
"""

from __future__ import annotations
from typing import Dict
import pandas as pd
from config import CENARIOS, ANOS_SIMULACAO, MESES_SIMULACAO, DIAS_UTEIS_SIMULACAO, DIAS_UTEIS_POR_ANO


def annual_to_monthly(annual_rate: float) -> float:
    """Converte taxa anual para mensal."""
    return (1.0 + annual_rate) ** (1.0 / 12.0) - 1.0


def annual_to_daily(annual_rate: float, days_per_year: int = DIAS_UTEIS_POR_ANO) -> float:
    """Converte taxa anual para diária."""
    return (1.0 + annual_rate) ** (1.0 / days_per_year) - 1.0


def _build_scenario_dataframe(cenario_key: str, granularity: str = "daily") -> pd.DataFrame:
    """
    Função unificada para construir DataFrames de cenários.
    
    Args:
        cenario_key: Chave do cenário em CENARIOS
        granularity: "monthly" ou "daily"
    """
    if cenario_key not in CENARIOS:
        raise ValueError(f"Cenário '{cenario_key}' não encontrado. Disponíveis: {list(CENARIOS.keys())}")
    
    cenario = CENARIOS[cenario_key]
    
    if granularity == "monthly":
        return _build_monthly_dataframe(cenario)
    else:  # daily
        return _build_daily_dataframe(cenario)


def _build_monthly_dataframe(cenario) -> pd.DataFrame:
    """Constrói DataFrame mensal para um cenário."""
    # Expande taxas anuais para meses
    selic_aa = []
    ipca_aa = []
    years = []
    
    for year_idx, (selic, ipca) in enumerate(zip(cenario.selic_por_ano, cenario.ipca_por_ano)):
        selic_aa.extend([selic] * 12)
        ipca_aa.extend([ipca] * 12)
        years.extend([2025 + year_idx] * 12)
    
    # Trunca para o número exato de meses
    selic_aa = selic_aa[:MESES_SIMULACAO]
    ipca_aa = ipca_aa[:MESES_SIMULACAO]
    years = years[:MESES_SIMULACAO]
    
    return pd.DataFrame({
        "scenario": [cenario.nome] * MESES_SIMULACAO,
        "month_index": list(range(1, MESES_SIMULACAO + 1)),
        "year": years,
        "selic_aa": selic_aa,
        "ipca_aa": ipca_aa,
        "selic_m": [annual_to_monthly(x) for x in selic_aa],
        "ipca_m": [annual_to_monthly(x) for x in ipca_aa],
    })


def _build_daily_dataframe(cenario) -> pd.DataFrame:
    """Constrói DataFrame diário para um cenário."""
    # Expande taxas anuais para dias
    selic_aa = []
    ipca_aa = []
    years = []
    
    for year_idx, (selic, ipca) in enumerate(zip(cenario.selic_por_ano, cenario.ipca_por_ano)):
        selic_aa.extend([selic] * DIAS_UTEIS_POR_ANO)
        ipca_aa.extend([ipca] * DIAS_UTEIS_POR_ANO)
        years.extend([2025 + year_idx] * DIAS_UTEIS_POR_ANO)
    
    # Trunca para o número exato de dias
    selic_aa = selic_aa[:DIAS_UTEIS_SIMULACAO]
    ipca_aa = ipca_aa[:DIAS_UTEIS_SIMULACAO]
    years = years[:DIAS_UTEIS_SIMULACAO]
    
    return pd.DataFrame({
        "scenario": [cenario.nome] * DIAS_UTEIS_SIMULACAO,
        "day_index": list(range(1, DIAS_UTEIS_SIMULACAO + 1)),
        "year": years,
        "selic_aa": selic_aa,
        "ipca_aa": ipca_aa,
        "selic_d": [annual_to_daily(x) for x in selic_aa],
        "ipca_d": [annual_to_daily(x) for x in ipca_aa],
    })


# Funções principais (interface pública)
def build_scenario_from_config(cenario_key: str, include_daily_columns: bool = False) -> pd.DataFrame:
    """Constrói cenário mensal a partir da configuração."""
    return _build_scenario_dataframe(cenario_key, "monthly")


def build_scenario_daily_from_config(cenario_key: str) -> pd.DataFrame:
    """Constrói cenário diário a partir da configuração."""
    return _build_scenario_dataframe(cenario_key, "daily")


def get_all_scenarios_daily() -> Dict[str, pd.DataFrame]:
    """Retorna todos os cenários em versão diária."""
    return {
        CENARIOS[key].nome: build_scenario_daily_from_config(key) 
        for key in CENARIOS.keys()
    }


def get_all_scenarios(include_daily_columns: bool = False) -> Dict[str, pd.DataFrame]:
    """Retorna todos os cenários em versão mensal."""
    return {
        CENARIOS[key].nome: build_scenario_from_config(key, include_daily_columns) 
        for key in CENARIOS.keys()
    }


def list_available_scenarios() -> Dict[str, str]:
    """Lista cenários disponíveis com descrições."""
    return {key: cenario.descricao for key, cenario in CENARIOS.items()}


# Funções de compatibilidade (simplificadas)
def scenario_manutencao(include_daily_columns: bool = False) -> pd.DataFrame:
    """Cenário 1 - Manutenção."""
    return build_scenario_from_config("Manutencao", include_daily_columns)


def scenario_manutencao_daily() -> pd.DataFrame:
    """Cenário 1 - Manutenção (diário)."""
    return build_scenario_daily_from_config("Manutencao")


def scenario_aperto(include_daily_columns: bool = False) -> pd.DataFrame:
    """Cenário 2 - Aperto."""
    return build_scenario_from_config("Aperto", include_daily_columns)


def scenario_aperto_daily() -> pd.DataFrame:
    """Cenário 2 - Aperto (diário)."""
    return build_scenario_daily_from_config("Aperto")


def scenario_afrouxamento(include_daily_columns: bool = False) -> pd.DataFrame:
    """Cenário 3 - Afrouxamento."""
    return build_scenario_from_config("Afrouxamento", include_daily_columns)


def scenario_afrouxamento_daily() -> pd.DataFrame:
    """Cenário 3 - Afrouxamento (diário)."""
    return build_scenario_daily_from_config("Afrouxamento")


__all__ = [
    "annual_to_monthly",
    "annual_to_daily",
    "build_scenario_from_config",
    "build_scenario_daily_from_config",
    "get_all_scenarios",
    "get_all_scenarios_daily",
    "list_available_scenarios",
    "scenario_manutencao",
    "scenario_manutencao_daily",
    "scenario_aperto",
    "scenario_aperto_daily",
    "scenario_afrouxamento",
    "scenario_afrouxamento_daily",
]
