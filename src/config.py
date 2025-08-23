"""
Configurações centralizadas do projeto.
"""

# Capital inicial padrão para todas as simulações
CAPITAL_INICIAL = 100_000.0

# Parâmetros temporais da simulação
ANOS_SIMULACAO = 3           # Número de anos para simular
DIAS_UTEIS_POR_ANO = 252     # Padrão do mercado brasileiro
MESES_POR_ANO = 12

# Parâmetros de custódia e impostos
TAXA_CUSTODIA_ANUAL = 0.002  # 0,2% a.a.
TR_MENSAL_FIXA = 0.0017     # 0,17% a.m. para poupança

# Parâmetros de mercado
SPREAD_CDI_SELIC = -0.001   # CDI fica 0,1 p.p. abaixo da Selic (conforme B3)

# Parâmetros calculados automaticamente
MESES_SIMULACAO = ANOS_SIMULACAO * MESES_POR_ANO        # 36 meses para 3 anos
DIAS_UTEIS_SIMULACAO = ANOS_SIMULACAO * DIAS_UTEIS_POR_ANO  # 756 dias úteis para 3 anos

# =============================================================================
# CONFIGURAÇÕES DOS CENÁRIOS ECONÔMICOS
# =============================================================================

CENARIOS_CONFIG = {
    "Manutencao": {
        "nome": "Cenario 1 - Manutencao",
        "descricao": f"Selic mantida em 15% a.a. e IPCA em 4,5% a.a. por {ANOS_SIMULACAO} anos",
        "selic_por_ano": [0.15] * ANOS_SIMULACAO,  # 15% mantido por todos os anos
        "ipca_por_ano": [0.045] * ANOS_SIMULACAO,  # 4,5% mantido por todos os anos
    },
    
    "Aperto": {
        "nome": "Cenario 2 - Aperto",
        "descricao": "Aperto monetário: Selic sobe gradualmente; IPCA acelera",
        "selic_por_ano": [0.15, 0.165, 0.17][:ANOS_SIMULACAO],  # Ajusta automaticamente
        "ipca_por_ano": [0.045, 0.05, 0.055][:ANOS_SIMULACAO],  # Ajusta automaticamente
    },
    
    "Afrouxamento": {
        "nome": "Cenario 3 - Afrouxamento",
        "descricao": "Afrouxamento monetário: Selic cai gradualmente; IPCA controlado",
        "selic_por_ano": [0.15, 0.13, 0.11][:ANOS_SIMULACAO],  # Ajusta automaticamente
        "ipca_por_ano": [0.04] * ANOS_SIMULACAO,  # 4% mantido por todos os anos
    },
    
    # =============================================================================
    # CENÁRIOS ADICIONAIS
    # =============================================================================
    
    # "Recessao": {
    #     "nome": "Cenario 4 - Recessao",
    #     "descricao": "Cenário recessivo: Selic muito baixa, IPCA controlado",
    #     "selic_por_ano": [0.15, 0.08, 0.05][:ANOS_SIMULACAO],
    #     "ipca_por_ano": [0.045, 0.02, 0.015][:ANOS_SIMULACAO],
    # },
    
    # "Crise": {
    #     "nome": "Cenario 5 - Crise",
    #     "descricao": "Cenário de crise: Selic alta, IPCA descontrolado",
    #     "selic_por_ano": [0.15, 0.25, 0.30][:ANOS_SIMULACAO],
    #     "ipca_por_ano": [0.045, 0.12, 0.18][:ANOS_SIMULACAO],
    # },
    
    # "Expansao": {
    #     "nome": "Cenario 6 - Expansao",
    #     "descricao": "Cenário expansivo: Selic baixa, crescimento econômico",
    #     "selic_por_ano": [0.15, 0.10, 0.06][:ANOS_SIMULACAO],
    #     "ipca_por_ano": [0.045, 0.035, 0.025][:ANOS_SIMULACAO],
    # },
}
