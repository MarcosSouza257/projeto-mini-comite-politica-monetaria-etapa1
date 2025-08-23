"""
Configurações centralizadas do projeto.
"""

from dataclasses import dataclass
from typing import List

# Capital inicial padrão para todas as simulações
CAPITAL_INICIAL = 100_000.0

# Parâmetros temporais da simulação
ANOS_SIMULACAO = 3           # Número de anos para simular
DIAS_UTEIS_POR_ANO = 252     # Padrão do mercado brasileiro
MESES_POR_ANO = 12

# Parâmetros de custódia e impostos
TAXA_CUSTODIA_ANUAL = 0.002  # 0,2% a.a.
ALIQUOTA_IR = 0.15          # 15% para investimentos (ajustado automaticamente por prazo)
TR_MENSAL_FIXA = 0.0017     # 0,17% a.m. para poupança

# Parâmetros calculados automaticamente
MESES_SIMULACAO = ANOS_SIMULACAO * MESES_POR_ANO        # 36 meses para 3 anos
DIAS_UTEIS_SIMULACAO = ANOS_SIMULACAO * DIAS_UTEIS_POR_ANO  # 756 dias úteis para 3 anos

# =============================================================================
# DEFINIÇÃO DE CENÁRIOS ECONÔMICOS
# =============================================================================

@dataclass(frozen=True)
class CenarioEconomico:
    """Define um cenário econômico com trajetórias de Selic e IPCA flexível por anos."""
    nome: str
    descricao: str
    selic_por_ano: List[float]  # Lista de taxas Selic por ano (decimal: 0.15 = 15%)
    ipca_por_ano: List[float]   # Lista de taxas IPCA por ano
    
    def __post_init__(self):
        """Valida que as listas têm o tamanho correto."""
        if len(self.selic_por_ano) != ANOS_SIMULACAO:
            raise ValueError(f"selic_por_ano deve ter {ANOS_SIMULACAO} elementos, recebeu {len(self.selic_por_ano)}")
        if len(self.ipca_por_ano) != ANOS_SIMULACAO:
            raise ValueError(f"ipca_por_ano deve ter {ANOS_SIMULACAO} elementos, recebeu {len(self.ipca_por_ano)}")
    
    # Propriedades para compatibilidade com cenários de 3 anos
    @property
    def selic_ano1(self) -> float:
        """Taxa Selic do primeiro ano (compatibilidade)."""
        return self.selic_por_ano[0] if len(self.selic_por_ano) > 0 else 0.0
    
    @property
    def selic_ano2(self) -> float:
        """Taxa Selic do segundo ano (compatibilidade)."""
        return self.selic_por_ano[1] if len(self.selic_por_ano) > 1 else self.selic_ano1
    
    @property
    def selic_ano3(self) -> float:
        """Taxa Selic do terceiro ano (compatibilidade)."""
        return self.selic_por_ano[2] if len(self.selic_por_ano) > 2 else self.selic_ano2
    
    @property
    def ipca_ano1(self) -> float:
        """Taxa IPCA do primeiro ano (compatibilidade)."""
        return self.ipca_por_ano[0] if len(self.ipca_por_ano) > 0 else 0.0
    
    @property
    def ipca_ano2(self) -> float:
        """Taxa IPCA do segundo ano (compatibilidade)."""
        return self.ipca_por_ano[1] if len(self.ipca_por_ano) > 1 else self.ipca_ano1
    
    @property
    def ipca_ano3(self) -> float:
        """Taxa IPCA do terceiro ano (compatibilidade)."""
        return self.ipca_por_ano[2] if len(self.ipca_por_ano) > 2 else self.ipca_ano2

# =============================================================================
# CENÁRIOS ECONÔMICOS
# =============================================================================

CENARIOS = {
    "Manutencao": CenarioEconomico(
        nome="Cenario 1 - Manutencao",
        descricao=f"Selic mantida em 15% a.a. e IPCA em 4,5% a.a. por {ANOS_SIMULACAO} anos",
        selic_por_ano=[0.15] * ANOS_SIMULACAO,  # 15% mantido por todos os anos
        ipca_por_ano=[0.045] * ANOS_SIMULACAO,  # 4,5% mantido por todos os anos
    ),
    
    "Aperto": CenarioEconomico(
        nome="Cenario 2 - Aperto",
        descricao="Aperto monetário: Selic sobe gradualmente; IPCA acelera",
        selic_por_ano=[0.15, 0.165, 0.17][:ANOS_SIMULACAO],  # Ajusta automaticamente para o número de anos
        ipca_por_ano=[0.045, 0.05, 0.055][:ANOS_SIMULACAO],  # Ajusta automaticamente para o número de anos
    ),
    
    "Afrouxamento": CenarioEconomico(
        nome="Cenario 3 - Afrouxamento", 
        descricao="Afrouxamento monetário: Selic cai gradualmente; IPCA controlado",
        selic_por_ano=[0.15, 0.13, 0.11][:ANOS_SIMULACAO],  # Ajusta automaticamente para o número de anos
        ipca_por_ano=[0.04] * ANOS_SIMULACAO,                # 4% mantido por todos os anos
    ),
}

# CENARIOS["recessao"] = CenarioEconomico(
#     nome="Cenario 4 - Recessao",
#     descricao="Cenário recessivo: Selic muito baixa, IPCA controlado",
#     selic_ano1=0.15,   # 15% em 2025
#     selic_ano2=0.08,   # 8% em 2026 (corte agressivo)
#     selic_ano3=0.05,   # 5% em 2027 (piso histórico)
#     ipca_ano1=0.045,   # 4,5% em 2025
#     ipca_ano2=0.02,    # 2% em 2026 (desaceleração)
#     ipca_ano3=0.015,   # 1,5% em 2027 (abaixo da meta)
# )

# CENARIOS["hiperinflacao"] = CenarioEconomico(
#     nome="Cenario 5 - Hiperinflacao",
#     descricao="Cenário extremo: Selic muito alta, IPCA descontrolado",
#     selic_ano1=0.15,   # 15% em 2025
#     selic_ano2=0.25,   # 25% em 2026 (choque de juros)
#     selic_ano3=0.30,   # 30% em 2027 (emergencial)
#     ipca_ano1=0.045,   # 4,5% em 2025
#     ipca_ano2=0.12,    # 12% em 2026 (descontrole)
#     ipca_ano3=0.18,    # 18% em 2027 (crise)
# )
