"""
Configurações centralizadas do projeto.
"""

from dataclasses import dataclass
from typing import List

# Capital inicial padrão para todas as simulações
CAPITAL_INICIAL = 100_000.0

# Parâmetros de custódia e impostos
TAXA_CUSTODIA_ANUAL = 0.002  # 0,2% a.a.
ALIQUOTA_IR_3_ANOS = 0.15    # 15% para investimentos de 3 anos
DIAS_UTEIS_POR_ANO = 252     # Padrão do mercado brasileiro
MESES_POR_ANO = 12
TR_MENSAL_FIXA = 0.0017      # 0,17% a.m. para poupança

# =============================================================================
# DEFINIÇÃO DE CENÁRIOS ECONÔMICOS
# =============================================================================

@dataclass(frozen=True)
class CenarioEconomico:
    """Define um cenário econômico com trajetórias de Selic e IPCA por 3 anos."""
    nome: str
    descricao: str
    selic_ano1: float  # Taxa Selic para 2025 (decimal: 0.15 = 15%)
    selic_ano2: float  # Taxa Selic para 2026
    selic_ano3: float  # Taxa Selic para 2027
    ipca_ano1: float   # IPCA para 2025
    ipca_ano2: float   # IPCA para 2026
    ipca_ano3: float   # IPCA para 2027
    
    @property
    def selic_por_ano(self) -> List[float]:
        """Retorna lista com as taxas Selic dos 3 anos."""
        return [self.selic_ano1, self.selic_ano2, self.selic_ano3]
    
    @property
    def ipca_por_ano(self) -> List[float]:
        """Retorna lista com as taxas IPCA dos 3 anos."""
        return [self.ipca_ano1, self.ipca_ano2, self.ipca_ano3]

# =============================================================================
# CENÁRIOS ECONÔMICOS
# =============================================================================

CENARIOS = {
    "Manutencao": CenarioEconomico(
        nome="Cenario 1 - Manutencao",
        descricao="Selic mantida em 15% a.a. e IPCA em 4,5% a.a. por 3 anos",
        selic_ano1=0.15,   # 15% em 2025
        selic_ano2=0.15,   # 15% em 2026  
        selic_ano3=0.15,   # 15% em 2027
        ipca_ano1=0.045,   # 4,5% em 2025
        ipca_ano2=0.045,   # 4,5% em 2026
        ipca_ano3=0.045,   # 4,5% em 2027
    ),
    
    "Aperto": CenarioEconomico(
        nome="Cenario 2 - Aperto",
        descricao="Aperto monetário: Selic sobe para 16,5% e 17%; IPCA acelera",
        selic_ano1=0.15,   # 15% em 2025
        selic_ano2=0.165,  # 16,5% em 2026
        selic_ano3=0.17,   # 17% em 2027
        ipca_ano1=0.045,   # 4,5% em 2025
        ipca_ano2=0.05,    # 5,0% em 2026
        ipca_ano3=0.055,   # 5,5% em 2027
    ),
    
    "Afrouxamento": CenarioEconomico(
        nome="Cenario 3 - Afrouxamento",
        descricao="Afrouxamento monetário: Selic cai para 13% e 11%; IPCA em 4%",
        selic_ano1=0.15,   # 15% em 2025
        selic_ano2=0.13,   # 13% em 2026
        selic_ano3=0.11,   # 11% em 2027
        ipca_ano1=0.04,    # 4% em 2025
        ipca_ano2=0.04,    # 4% em 2026
        ipca_ano3=0.04,    # 4% em 2027
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
