from __future__ import annotations

from typing import Dict, Optional

import matplotlib.pyplot as plt


def plot_summary_bar(df_summary, title: str = "Resumo por Produto", save_path: Optional[str] = None, show: bool = False) -> None:
    """Plota barras com VF líquido por produto (DataFrame produzido em simulate.py).

    Espera colunas: 'produto', 'vf_liquido'.
    """
    fig, ax = plt.subplots(figsize=(8, 4.5))
    df_plot = df_summary.sort_values("vf_liquido", ascending=True)
    ax.barh(df_plot["produto"], df_plot["vf_liquido"], color="#4C78A8")
    ax.set_title(title)
    ax.set_xlabel("VF Líquido (R$)")
    ax.set_ylabel("Produto")
    for i, v in enumerate(df_plot["vf_liquido" ]):
        ax.text(v, i, f" R$ {v:,.2f}", va="center", ha="left")
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
    if show:
        plt.show()
    plt.close(fig)


def plot_timeline(product_result: dict, title: str = "Evolução Mensal", save_path: Optional[str] = None, show: bool = False) -> None:
    """Plota a evolução mensal do saldo para um produto (saída de products.py).

    Usa a coluna 'saldo_pos_custodia' da timeline.
    """
    df = product_result["timeline"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(df["periodo"], df["saldo_pos_custodia"], label=product_result["produto"], color="#72B7B2")
    ax.set_title(title)
    ax.set_xlabel("Período (mês)")
    ax.set_ylabel("Saldo pós-custódia (R$)")
    ax.legend()
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
    if show:
        plt.show()
    plt.close(fig)


def plot_all_scenarios_summary(results_by_scenario: Dict[str, object], save_dir: Optional[str] = None, show: bool = False) -> None:
    """Recebe o dicionário {nome_cenário: df_resumo} e plota um gráfico por cenário.

    - save_dir: se informado, salva cada figura como PNG dentro do diretório.
    """
    for scen_name, df_summary in results_by_scenario.items():
        title = f"{scen_name} — VF Líquido por Produto"
        path = f"{save_dir}/{scen_name.replace(' ', '_').lower()}_summary.png" if save_dir else None
        plot_summary_bar(df_summary, title=title, save_path=path, show=show)


__all__ = [
    "plot_summary_bar",
    "plot_timeline",
    "plot_all_scenarios_summary",
]


