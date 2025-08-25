"""
Funções para cálculo de impostos e taxas.
"""

# Tabela regressiva do Imposto de Renda (conforme legislação brasileira)
TABELA_IR = [
    {"dias_min": 0,   "dias_max": 180, "aliquota": 0.225},  # 22,5% até 180 dias
    {"dias_min": 181, "dias_max": 360, "aliquota": 0.20},   # 20% de 181 a 360 dias  
    {"dias_min": 361, "dias_max": 720, "aliquota": 0.175},  # 17,5% de 361 a 720 dias
    {"dias_min": 721, "dias_max": 9999, "aliquota": 0.15}   # 15% acima de 720 dias
]


def get_ir_rate_by_days(dias: int) -> float:
    """Retorna a alíquota de IR baseada no número de dias de aplicação.
    
    Tabela regressiva:
    - Até 180 dias: 22,5%
    - De 181 a 360 dias: 20%
    - De 361 a 720 dias: 17,5%
    - Acima de 720 dias: 15%
    
    Args:
        dias: Número de dias de aplicação
        
    Returns:
        float: Alíquota de IR (ex: 0.225 para 22,5%)
    """
    for faixa in TABELA_IR:
        if faixa["dias_min"] <= dias <= faixa["dias_max"]:
            return faixa["aliquota"]
    
    # Fallback para casos extremos (mais de 9999 dias)
    return TABELA_IR[-1]["aliquota"]  # 15%


def get_ir_rate_by_periods(periodo: int, periods_per_year: int) -> float:
    """Retorna a alíquota de IR baseada no período de aplicação.
    
    Converte períodos (dias úteis ou meses) para dias corridos conforme 
    a tabela regressiva do IR que usa dias de calendário.
    
    Args:
        periodo: Número do período (0-based)
        periods_per_year: Períodos por ano (12 para mensal, 252 para diário)
        
    Returns:
        float: Alíquota de IR
    """
    # Converte período para dias corridos
    if periods_per_year == 252:  # Simulação diária
        # Conversão dias úteis → dias corridos: 365.25 dias/ano ÷ 252 dias úteis/ano
        fator_conversao = 365.25 / 252  # ≈ 1.449
        dias_corridos = int((periodo + 1) * fator_conversao)
    else:  # Simulação mensal
        dias_corridos = (periodo + 1) * 30  # Aproximação de 30 dias por mês
    
    return get_ir_rate_by_days(dias_corridos)


def calculate_ir_provision(valor_inicial: float, saldo_atual: float, periodo: int, periods_per_year: int, ir_exempt: bool = False) -> float:
    """Calcula a provisão de IR baseada no tempo de aplicação.
    
    Args:
        valor_inicial: Valor inicial investido
        saldo_atual: Saldo atual bruto
        periodo: Período atual (0-based)
        periods_per_year: Períodos por ano
        ir_exempt: Se o produto é isento de IR
        
    Returns:
        float: Valor da provisão de IR
    """
    if ir_exempt or saldo_atual <= valor_inicial:
        return 0.0
    
    rendimento = saldo_atual - valor_inicial
    aliquota_ir = get_ir_rate_by_periods(periodo, periods_per_year)
    
    return rendimento * aliquota_ir


def get_ir_description_by_days(dias: int) -> str:
    """Retorna descrição da faixa de IR baseada no número de dias.
    
    Args:
        dias: Número de dias de aplicação
        
    Returns:
        str: Descrição da faixa (ex: "22,5% (até 180 dias)")
    """
    aliquota = get_ir_rate_by_days(dias)
    
    if dias <= 180:
        return f"{aliquota:.1%} (até 180 dias)"
    elif dias <= 360:
        return f"{aliquota:.1%} (181-360 dias)"
    elif dias <= 720:
        return f"{aliquota:.1%} (361-720 dias)"
    else:
        return f"{aliquota:.1%} (acima de 720 dias)"


def get_ir_schedule_summary() -> str:
    """Retorna resumo da tabela regressiva de IR.
    
    Returns:
        str: Resumo formatado da tabela
    """
    summary = "Tabela Regressiva do Imposto de Renda:\n"
    summary += "• Até 180 dias: 22,5%\n"
    summary += "• De 181 a 360 dias: 20,0%\n"
    summary += "• De 361 a 720 dias: 17,5%\n"
    summary += "• Acima de 720 dias: 15,0%\n"
    return summary