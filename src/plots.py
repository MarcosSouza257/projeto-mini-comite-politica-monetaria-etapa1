from __future__ import annotations

import os
from typing import Dict, Optional
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio


def plot_summary_bar(df_summary, title: str = "Resumo por Produto", save_path: Optional[str] = None, show: bool = False) -> go.Figure:
    """Plota barras com VF líquido por produto (DataFrame produzido em simulate.py).

    Espera colunas: 'produto', 'vf_liquido'.
    """
    df_plot = df_summary.sort_values("vf_liquido", ascending=True)
    
    # Criar gráfico de barras horizontais
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_plot["produto"],
        x=df_plot["vf_liquido"],
        orientation='h',
        marker_color='#4C78A8',
        text=[f'R$ {v:,.0f}' for v in df_plot["vf_liquido"]],
        textposition='outside',
        textfont=dict(size=11),
        hovertemplate='<b>%{y}</b><br>VF Líquido: R$ %{x:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2E86AB'}
        },
        xaxis_title="VF Líquido (R$)",
        yaxis_title="Produto",
        height=400,
        width=800,
        margin=dict(l=20, r=80, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        xaxis=dict(
            tickformat=',.0f',
            gridcolor='lightgray',
            gridwidth=0.5
        ),
        yaxis=dict(
            tickfont=dict(size=11)
        )
    )
    
    if save_path:
        pio.write_image(fig, save_path, width=800, height=400, scale=2)
    
    if show:
        fig.show()
    
    return fig


def plot_timeline(product_result: dict, title: str = "Evolução Temporal", save_path: Optional[str] = None, show: bool = False) -> go.Figure:
    """Plota a evolução temporal do saldo para um produto (saída de products.py).

    Usa as colunas 'saldo_bruto', 'provisao_ir' e 'saldo_liquido_estimado' da timeline.
    """
    df = product_result["timeline"]
    produto_nome = product_result["produto"]
    
    fig = go.Figure()
    
    # Linha do saldo bruto
    fig.add_trace(go.Scatter(
        x=df["periodo"],
        y=df["saldo_bruto"],
        mode='lines',
        name='Saldo Bruto',
        line=dict(color='#2E86AB', width=2),
        hovertemplate='<b>Saldo Bruto</b><br>Período: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Linha do saldo líquido estimado
    fig.add_trace(go.Scatter(
        x=df["periodo"],
        y=df["saldo_liquido_estimado"],
        mode='lines',
        name='Saldo Líquido',
        line=dict(color='#A23B72', width=2),
        hovertemplate='<b>Saldo Líquido</b><br>Período: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Área da provisão de IR
    fig.add_trace(go.Scatter(
        x=df["periodo"],
        y=df["provisao_ir"],
        mode='lines',
        name='Provisão IR',
        line=dict(color='#F18F01', width=1),
        fill='tozeroy',
        fillcolor='rgba(241, 143, 1, 0.2)',
        hovertemplate='<b>Provisão IR</b><br>Período: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f"{title} - {produto_nome}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2E86AB'}
        },
        xaxis_title="Período (dias úteis)",
        yaxis_title="Valor (R$)",
        height=500,
        width=900,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        xaxis=dict(
            gridcolor='lightgray',
            gridwidth=0.5,
            showline=True,
            linecolor='gray'
        ),
        yaxis=dict(
            tickformat=',.0f',
            gridcolor='lightgray',
            gridwidth=0.5,
            showline=True,
            linecolor='gray'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    
    if save_path:
        pio.write_image(fig, save_path, width=900, height=500, scale=2)
    
    if show:
        fig.show()
    
    return fig


def plot_all_scenarios_summary(results_by_scenario: Dict[str, object], save_dir: Optional[str] = None, show: bool = False) -> None:
    """Recebe o dicionário {nome_cenário: df_resumo} e plota um gráfico por cenário.

    - save_dir: se informado, salva cada figura como PNG dentro do diretório.
    """
    for scen_name, df_summary in results_by_scenario.items():
        title = f"{scen_name} — VF Líquido por Produto"
        path = f"{save_dir}/{scen_name.replace(' ', '_').lower()}_summary.png" if save_dir else None
        plot_summary_bar(df_summary, title=title, save_path=path, show=show)


def plot_comparison_all_scenarios(results_by_scenario: Dict[str, object], save_path: Optional[str] = None, show: bool = False) -> go.Figure:
    """Cria gráfico comparativo de todos os cenários em uma única visualização."""
    
    fig = go.Figure()
    
    # Cores para cada cenário
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#8E44AD']
    
    for i, (scen_name, df_summary) in enumerate(results_by_scenario.items()):
        df_plot = df_summary.sort_values("vf_liquido", ascending=False)
        
        fig.add_trace(go.Bar(
            name=scen_name,
            x=df_plot["produto"],
            y=df_plot["vf_liquido"],
            marker_color=colors[i % len(colors)],
            text=[f'R$ {v:,.0f}' for v in df_plot["vf_liquido"]],
            textposition='outside',
            textfont=dict(size=10),
            hovertemplate=f'<b>{scen_name}</b><br>%{{x}}<br>VF Líquido: R$ %{{y:,.2f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': "Comparação de VF Líquido por Cenário",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E86AB'}
        },
        xaxis_title="Produtos",
        yaxis_title="VF Líquido (R$)",
        barmode='group',
        height=600,
        width=1000,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        xaxis=dict(
            tickangle=45,
            gridcolor='lightgray',
            gridwidth=0.5
        ),
        yaxis=dict(
            tickformat=',.0f',
            gridcolor='lightgray',
            gridwidth=0.5
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    if save_path:
        pio.write_image(fig, save_path, width=1000, height=600, scale=2)
    
    if show:
        fig.show()
    
    return fig


def plot_ir_evolution(product_result: dict, save_path: Optional[str] = None, show: bool = False) -> go.Figure:
    """Plota a evolução da alíquota de IR ao longo do tempo."""
    
    df = product_result["timeline"]
    produto_nome = product_result["produto"]
    
    # Calcular alíquota efetiva de IR
    ganho = df["saldo_bruto"] - df["saldo_bruto"].iloc[0]
    aliquota_efetiva = df["provisao_ir"] / ganho.replace(0, 1)  # Evitar divisão por zero
    aliquota_efetiva = aliquota_efetiva.fillna(0)
    
    fig = go.Figure()
    
    # Linha da alíquota de IR
    fig.add_trace(go.Scatter(
        x=df["periodo"],
        y=aliquota_efetiva * 100,  # Converter para percentual
        mode='lines',
        name='Alíquota IR Efetiva',
        line=dict(color='#C73E1D', width=2),
        hovertemplate='<b>Alíquota IR</b><br>Período: %{x}<br>Taxa: %{y:.1f}%<extra></extra>'
    ))
    
    # Adicionar linhas de referência das faixas de IR
    faixas_ir = [
        (0, 180, 22.5, "22,5% (0-180 dias)"),
        (181, 360, 20.0, "20% (181-360 dias)"),
        (361, 720, 17.5, "17,5% (361-720 dias)"),
        (721, len(df), 15.0, "15% (721+ dias)")
    ]
    
    for inicio, fim, taxa, nome in faixas_ir:
        if inicio < len(df):
            fim_real = min(fim, len(df) - 1)
            fig.add_hline(
                y=taxa,
                line_dash="dash",
                line_color="gray",
                annotation_text=nome,
                annotation_position="bottom right"
            )
    
    fig.update_layout(
        title={
            'text': f"Evolução da Alíquota de IR - {produto_nome}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2E86AB'}
        },
        xaxis_title="Período (dias úteis)",
        yaxis_title="Alíquota IR (%)",
        height=400,
        width=800,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        xaxis=dict(
            gridcolor='lightgray',
            gridwidth=0.5
        ),
        yaxis=dict(
            gridcolor='lightgray',
            gridwidth=0.5,
            range=[0, 25]  # 0% a 25%
        )
    )
    
    if save_path:
        pio.write_image(fig, save_path, width=800, height=400, scale=2)
    
    if show:
        fig.show()
    
    return fig


def plot_scenario_individual(scenario_name: str, df_summary, save_path: Optional[str] = None, show: bool = False) -> go.Figure:
    """Cria gráfico individual para um cenário específico com todos os títulos."""
    
    df_plot = df_summary.sort_values("vf_liquido", ascending=True)
    
    # Cores diferenciadas para cada produto
    colors = {
        'LCI': '#2E86AB',
        'Tesouro Selic': '#A23B72', 
        'CDB 100% CDI': '#F18F01',
        'Tesouro Prefixado': '#C73E1D',
        'Tesouro IPCA+': '#6A994E',
        'Poupanca': '#8E44AD'
    }
    
    # Mapear cores aos produtos
    bar_colors = [colors.get(produto, '#95A5A6') for produto in df_plot["produto"]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_plot["produto"],
        x=df_plot["vf_liquido"],
        orientation='h',
        marker_color=bar_colors,
        text=[f'R$ {v:,.0f}' for v in df_plot["vf_liquido"]],
        textposition='outside',
        textfont=dict(size=12, color='black'),
        hovertemplate='<b>%{y}</b><br>VF Líquido: R$ %{x:,.2f}<br>Rentabilidade: %{customdata:.1f}%<extra></extra>',
        customdata=((df_plot["vf_liquido"] / 100000) - 1) * 100  # Assumindo capital inicial de 100k
    ))
    
    # Adicionar linha de referência do capital inicial
    fig.add_vline(
        x=100000,
        line_dash="dash",
        line_color="gray",
        annotation_text="Capital Inicial",
        annotation_position="top"
    )
    
    fig.update_layout(
        title={
            'text': f"{scenario_name}<br><span style='font-size:14px'>Valor Futuro Líquido por Produto</span>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E86AB'}
        },
        xaxis_title="Valor Futuro Líquido (R$)",
        yaxis_title="Produtos de Investimento",
        height=500,
        width=900,
        margin=dict(l=150, r=100, t=100, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        xaxis=dict(
            tickformat=',.0f',
            gridcolor='lightgray',
            gridwidth=0.5,
            showline=True,
            linecolor='gray',
            range=[95000, df_plot["vf_liquido"].max() * 1.1]
        ),
        yaxis=dict(
            tickfont=dict(size=12),
            showline=True,
            linecolor='gray'
        ),
        showlegend=False
    )
    
    # Adicionar anotações com rentabilidade
    for i, (idx, row) in enumerate(df_plot.iterrows()):
        rentabilidade = ((row["vf_liquido"] / 100000) - 1) * 100
        fig.add_annotation(
            x=row["vf_liquido"] + 2000,
            y=i,
            text=f"{rentabilidade:+.1f}%",
            showarrow=False,
            font=dict(size=10, color='#666666'),
            xanchor='left'
        )
    
    if save_path:
        pio.write_image(fig, save_path, width=900, height=500, scale=2)
    
    if show:
        fig.show()
    
    return fig


def plot_evolution_by_scenario(results_data: Dict[str, Dict], save_dir: Optional[str] = None, show: bool = False) -> list[go.Figure]:
    """Cria gráficos de evolução temporal para cada cenário."""
    
    figures = []
    
    for scenario_name, data in results_data.items():
        # Nome limpo para arquivo
        clean_name = scenario_name.replace(' ', '_').replace('-', '').lower()
        save_path = f"{save_dir}/{clean_name}_evolucao.png" if save_dir else None
        
        fig = go.Figure()
        
        # Cores para cada produto
        colors = {
            'Tesouro_Selic': '#2E86AB',
            'CDB_100_CDI': '#F18F01', 
            'Tesouro_Prefixado': '#C73E1D',
            'Tesouro_IPCA_Plus': '#6A994E',
            'LCI': '#A23B72',
            'Poupanca': '#8E44AD'
        }
        
        # Plotar evolução de cada produto
        timelines = data.get("timelines", {})
        
        for produto_key, timeline_df in timelines.items():
            if len(timeline_df) > 0:
                # Nome limpo do produto para exibição
                produto_display = format_product_name(produto_key)
                color = colors.get(produto_key, '#95A5A6')
                
                # Criar datas baseadas no período (iniciando em 2025-01-01)
                dates = pd.date_range(start="2025-01-01", periods=len(timeline_df), freq='B').date
                
                # Linha do saldo líquido estimado
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=timeline_df["saldo_liquido_estimado"],
                    mode='lines',
                    name=produto_display,
                    line=dict(color=color, width=2),
                    hovertemplate=f'<b>{produto_display}</b><br>Data: %{{x}}<br>Saldo Líquido: R$ %{{y:,.2f}}<extra></extra>'
                ))
        
        # Adicionar linha de referência do capital inicial
        if len(timelines) > 0:
            fig.add_hline(
                y=100000,
                line_dash="dash",
                line_color="gray",
                annotation_text="Capital Inicial (R$ 100.000)",
                annotation_position="bottom right"
            )
        
        fig.update_layout(
            title={
                'text': f"Evolução Temporal - {scenario_name}<br><span style='font-size:14px'>Saldo Líquido ao Longo do Tempo</span>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#2E86AB'}
            },
            xaxis_title="Data",
            yaxis_title="Saldo Líquido (R$)",
            height=600,
            width=1000,
            margin=dict(l=60, r=60, t=100, b=80),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            xaxis=dict(
                gridcolor='lightgray',
                gridwidth=0.5,
                showline=True,
                linecolor='gray',
                tickformat='%d/%m/%Y',
                dtick='M3',  # Mostrar marcas a cada 3 meses
                tickangle=45  # Rotacionar datas em 45 graus
            ),
            yaxis=dict(
                tickformat=',.0f',
                gridcolor='lightgray',
                gridwidth=0.5,
                showline=True,
                linecolor='gray'
            ),
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.98,
                xanchor="left",
                x=1.02,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="lightgray",
                borderwidth=1
            ),
            hovermode='x unified'
        )
        
        if save_path:
            pio.write_image(fig, save_path, width=1000, height=600, scale=2)
        
        if show:
            fig.show()
        
        figures.append(fig)
    
    return figures


def plot_evolution_comparison(results_data: Dict[str, Dict], save_path: Optional[str] = None, show: bool = False) -> go.Figure:
    """Cria gráfico comparativo da evolução de um produto em todos os cenários."""
    
    fig = go.Figure()
    
    # Cores para cenários
    scenario_colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#8E44AD']
    
    # Escolher um produto para comparação (ex: Tesouro Selic)
    produto_referencia = "Tesouro_Selic"
    
    for i, (scenario_name, data) in enumerate(results_data.items()):
        timelines = data.get("timelines", {})
        
        if produto_referencia in timelines:
            timeline_df = timelines[produto_referencia]
            color = scenario_colors[i % len(scenario_colors)]
            
            # Criar datas baseadas no período (iniciando em 2025-01-01)
            dates = pd.date_range(start="2025-01-01", periods=len(timeline_df), freq='B').date
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=timeline_df["saldo_liquido_estimado"],
                mode='lines',
                name=scenario_name,
                line=dict(color=color, width=2),
                hovertemplate=f'<b>{scenario_name}</b><br>Data: %{{x}}<br>Saldo Líquido: R$ %{{y:,.2f}}<extra></extra>'
            ))
    
    # Linha de referência do capital inicial
    if results_data:
        fig.add_hline(
            y=100000,
            line_dash="dash",
            line_color="gray",
            annotation_text="Capital Inicial (R$ 100.000)",
            annotation_position="bottom right"
        )
    
    fig.update_layout(
        title={
            'text': f"Comparação de Evolução - Tesouro Selic<br><span style='font-size:14px'>Todos os Cenários Econômicos</span>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E86AB'}
        },
        xaxis_title="Data",
        yaxis_title="Saldo Líquido (R$)",
        height=600,
        width=1000,
        margin=dict(l=60, r=60, t=100, b=80),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        xaxis=dict(
            gridcolor='lightgray',
            gridwidth=0.5,
            showline=True,
            linecolor='gray',
            tickformat='%d/%m/%Y',
            dtick='M3',  # Mostrar marcas a cada 3 meses
            tickangle=45  # Rotacionar datas em 45 graus
        ),
        yaxis=dict(
            tickformat=',.0f',
            gridcolor='lightgray',
            gridwidth=0.5,
            showline=True,
            linecolor='gray'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        hovermode='x unified'
    )
    
    if save_path:
        pio.write_image(fig, save_path, width=1000, height=600, scale=2)
    
    if show:
        fig.show()
    
    return fig


def plot_all_scenarios_individual(results_by_scenario: Dict[str, object], save_dir: Optional[str] = None, show: bool = False) -> list[go.Figure]:
    """Cria um gráfico individual para cada cenário (total de 3 gráficos)."""
    
    figures = []
    
    for scen_name, df_summary in results_by_scenario.items():
        # Nome limpo para arquivo
        clean_name = scen_name.replace(' ', '_').replace('-', '').lower()
        save_path = f"{save_dir}/{clean_name}_individual.png" if save_dir else None
        
        fig = plot_scenario_individual(
            scenario_name=scen_name,
            df_summary=df_summary,
            save_path=save_path,
            show=show
        )
        
        figures.append(fig)
    
    return figures


def create_interactive_dashboard(results_by_scenario: Dict[str, object], save_path: Optional[str] = None, show: bool = False) -> go.Figure:
    """Cria dashboard interativo com múltiplos gráficos."""
    
    from plotly.subplots import make_subplots
    
    # Criar subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Comparação por Cenário", "Evolução Temporal", "Distribuição de Produtos", "Análise de Rentabilidade"),
        specs=[[{"type": "bar"}, {"type": "scatter"}],
               [{"type": "pie"}, {"type": "bar"}]]
    )
    
    # Cores para cenários
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    # Gráfico 1: Comparação por cenário (primeiro cenário como exemplo)
    primeiro_cenario = list(results_by_scenario.values())[0]
    df_plot = primeiro_cenario.sort_values("vf_liquido", ascending=True)
    
    fig.add_trace(
        go.Bar(
            y=df_plot["produto"],
            x=df_plot["vf_liquido"],
            orientation='h',
            marker_color='#2E86AB',
            name="VF Líquido",
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Gráfico 2: Evolução temporal (exemplo com primeiro produto)
    # Este seria mais complexo, simplificando para demonstração
    periodos = list(range(1, 757))  # 756 dias úteis
    valores_exemplo = [100000 * (1.15/252 + 1) ** i for i in periodos]
    
    fig.add_trace(
        go.Scatter(
            x=periodos,
            y=valores_exemplo,
            mode='lines',
            name="Evolução",
            line=dict(color='#A23B72'),
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Gráfico 3: Distribuição (pie chart)
    fig.add_trace(
        go.Pie(
            labels=df_plot["produto"],
            values=df_plot["vf_liquido"],
            marker_colors=colors[:len(df_plot)],
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Gráfico 4: Análise de rentabilidade
    rentabilidade = ((df_plot["vf_liquido"] / 100000) - 1) * 100  # Assumindo capital inicial de 100k
    
    fig.add_trace(
        go.Bar(
            x=df_plot["produto"],
            y=rentabilidade,
            marker_color='#F18F01',
            name="Rentabilidade %",
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Atualizar layout
    fig.update_layout(
        title={
            'text': "Dashboard Interativo - Análise de Investimentos",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2E86AB'}
        },
        height=800,
        width=1200,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=10)
    )
    
    # Atualizar eixos
    fig.update_xaxes(title_text="VF Líquido (R$)", row=1, col=1)
    fig.update_yaxes(title_text="Produtos", row=1, col=1)
    fig.update_xaxes(title_text="Período (dias)", row=1, col=2)
    fig.update_yaxes(title_text="Valor (R$)", row=1, col=2)
    fig.update_xaxes(title_text="Produtos", row=2, col=2)
    fig.update_yaxes(title_text="Rentabilidade (%)", row=2, col=2)
    
    if save_path:
        pio.write_html(fig, save_path)
    
    if show:
        fig.show()
    
    return fig


def plot_rentability_by_product(results_data: Dict[str, Dict], save_dir: Optional[str] = None, show: bool = False) -> list[go.Figure]:
    """Cria gráficos de evolução temporal da rentabilidade por produto (total 5 gráficos)."""
    
    figures = []
    
    # Produtos na ordem desejada
    produtos_ordem = ["Tesouro Selic", "Tesouro Prefixado", "Tesouro IPCA+", "CDB 100% CDI", "LCI", "Poupanca"]
    
    # Cores para cenários
    scenario_colors = {
        'Cenario 1 - Manutencao': '#2E86AB',
        'Cenario 2 - Aperto': '#A23B72', 
        'Cenario 3 - Afrouxamento': '#F18F01'
    }
    
    for produto in produtos_ordem:
        fig = go.Figure()
        
        # Procurar o produto em cada cenário
        for scenario_name, data in results_data.items():
            timelines = data.get("timelines", {})
            
            # Encontrar a chave correta do produto
            produto_key = None
            for key in timelines.keys():
                if format_product_name(key) == produto:
                    produto_key = key
                    break
            
            if produto_key and produto_key in timelines:
                timeline_df = timelines[produto_key]
                color = scenario_colors.get(scenario_name, '#95A5A6')
                
                # Criar datas baseadas no período (iniciando em 2025-01-01)
                dates = pd.date_range(start="2025-01-01", periods=len(timeline_df), freq='B').date
                
                # Calcular rentabilidade acumulada ao longo do tempo
                rentabilidade_temporal = ((timeline_df["saldo_liquido_estimado"] / 100000) - 1) * 100
                
                # Linha da evolução da rentabilidade
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=rentabilidade_temporal,
                    mode='lines',
                    name=scenario_name,
                    line=dict(color=color, width=2),
                    hovertemplate=f'<b>{scenario_name}</b><br>Data: %{{x}}<br>Rentabilidade: %{{y:.1f}}%<br>Saldo: R$ %{{customdata:,.2f}}<extra></extra>',
                    customdata=timeline_df["saldo_liquido_estimado"]
                ))
        
        # Linha de referência em 0%
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="gray",
            annotation_text="Sem ganho/perda",
            annotation_position="bottom right"
        )
        
        fig.update_layout(
            title={
                'text': f"Evolução da Rentabilidade: {produto}<br><span style='font-size:14px'>Comparação Temporal entre Cenários</span>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#2E86AB'}
            },
            xaxis_title="Data",
            yaxis_title="Rentabilidade Acumulada (%)",
            height=500,
            width=900,
            margin=dict(l=60, r=60, t=100, b=80),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            xaxis=dict(
                gridcolor='lightgray',
                gridwidth=0.5,
                showline=True,
                linecolor='gray',
                tickformat='%d/%m/%Y',
                dtick='M3',  # Mostrar marcas a cada 3 meses
                tickangle=45  # Rotacionar datas em 45 graus
            ),
            yaxis=dict(
                tickformat='.1f',
                ticksuffix='%',
                gridcolor='lightgray',
                gridwidth=0.5,
                showline=True,
                linecolor='gray'
            ),
            legend=dict(
                orientation="v",
                x=0.98,
                y=0.15,
                xanchor="right",
                yanchor="bottom",
                bgcolor="rgba(255,255,255,0.6)",  # fundo translúcido
                bordercolor="lightgray",
                borderwidth=1
            )
        )
        
        # Salvar gráfico
        if save_dir:
            produto_clean = produto.replace(' ', '_').replace('+', 'Plus').replace('%', 'pct')
            save_path = f"{save_dir}/{produto_clean.lower()}_rentabilidade_evolucao.png"
            pio.write_image(fig, save_path, width=900, height=500, scale=2)
        
        if show:
            fig.show()
        
        figures.append(fig)
    
    return figures


def format_product_name(produto_key: str) -> str:
    """Converte nomes de produtos para exibição nos gráficos."""
    if produto_key == 'Tesouro_IPCA_Plus':
        return 'Tesouro IPCA+'
    elif produto_key == 'CDB_100_CDI':
        return 'CDB 100% CDI'
    else:
        return produto_key.replace('_', ' ')


def generate_all_plots(results_data: Dict[str, Dict], args, fig_dir: str) -> None:
    """Centraliza toda a lógica de geração de gráficos baseada nos argumentos CLI."""
    
    # Verificar se deve gerar gráficos
    if not (args.save_figures or args.plotly or args.individual or args.evolucao or args.rentabilidade):
        return
    
    # Criar diretório de figuras
    os.makedirs(fig_dir, exist_ok=True)
    
    # Preparar dados para gráficos
    results_by_scenario = {name: data["summary"] for name, data in results_data.items()}
    
    if args.plotly or args.individual or args.evolucao or args.rentabilidade:
        # Gráficos Plotly interativos
        print("\n🎨 Gerando gráficos interativos com Plotly...")
        
        # Gráficos de evolução temporal
        if args.evolucao:
            evolution_figures = plot_evolution_by_scenario(
                results_data,
                save_dir=fig_dir,
                show=False
            )
            print(f"📈 {len(evolution_figures)} gráficos de evolução criados (um por cenário)")
            
            # Gráfico comparativo de evolução
            plot_evolution_comparison(
                results_data,
                save_path=f"{fig_dir}/evolucao_comparativa.png",
                show=False
            )
            print("📊 Gráfico comparativo de evolução criado")
        
        # Gráficos individuais por cenário
        if args.individual:
            individual_figures = plot_all_scenarios_individual(
                results_by_scenario,
                save_dir=fig_dir,
                show=False
            )
            print(f"📈 {len(individual_figures)} gráficos individuais criados (um por cenário)")
        
        # Gráficos de rentabilidade por produto
        if args.rentabilidade:
            rentability_figures = plot_rentability_by_product(
                results_data,  # Usar results completo com timelines
                save_dir=fig_dir,
                show=False
            )
            print(f"📊 {len(rentability_figures)} gráficos de evolução da rentabilidade criados (um por produto)")
        
        # Gráfico comparativo de todos os cenários
        if args.plotly and not args.individual and not args.evolucao:
            plot_comparison_all_scenarios(
                results_by_scenario, 
                save_path=f"{fig_dir}/comparacao_cenarios.png",
                show=False
            )
        
        # Dashboard interativo
        if args.dashboard:
            create_interactive_dashboard(
                results_by_scenario,
                save_path=f"{fig_dir}/dashboard_interativo.html",
                show=False
            )
            print(f"📊 Dashboard interativo salvo: {fig_dir}/dashboard_interativo.html")
        
        print(f"🎯 Gráficos Plotly salvos em: {os.path.abspath(fig_dir)}")
    else:
        # Gráficos tradicionais (Matplotlib)
        plot_all_scenarios_summary(results_by_scenario=results_by_scenario, save_dir=fig_dir, show=False)


__all__ = [
    "plot_summary_bar",
    "plot_timeline",
    "plot_all_scenarios_summary",
    "plot_comparison_all_scenarios",
    "plot_ir_evolution",
    "plot_scenario_individual",
    "plot_all_scenarios_individual",
    "plot_evolution_by_scenario",
    "plot_evolution_comparison",
    "plot_rentability_by_product",
    "create_interactive_dashboard",
    "generate_all_plots",
    "format_product_name"
]


