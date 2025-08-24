from __future__ import annotations

import argparse
import os
import sys
import pandas as pd


def _ensure_src_on_path() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(here, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def parse_args() -> argparse.Namespace:
    # Importa após garantir que src está no path
    _ensure_src_on_path()
    from src.config import CAPITAL_INICIAL
    
    parser = argparse.ArgumentParser(description="Executa simulações dos cenários e produtos.")
    parser.add_argument("--initial", type=float, default=CAPITAL_INICIAL, help="Valor inicial (R$)")
    parser.add_argument("--save-figures", action="store_true", help="Salvar gráficos em figures/")
    parser.add_argument("--fig-dir", type=str, default="figures", help="Diretório para salvar gráficos")
    parser.add_argument("--plotly", action="store_true", help="Usar Plotly para gráficos interativos")
    parser.add_argument("--dashboard", action="store_true", help="Gerar dashboard interativo HTML")
    parser.add_argument("--individual", action="store_true", help="Gerar gráfico individual para cada cenário")
    parser.add_argument("--evolucao", action="store_true", help="Gerar gráficos de evolução temporal")
    parser.add_argument("--rentabilidade", action="store_true", help="Gerar gráficos de rentabilidade por produto")
    parser.add_argument("--save-results", action="store_true", help="Salvar resumos em CSV (pasta data/)")
    parser.add_argument("--out-dir", type=str, default="data", help="Diretório para salvar resultados")
    return parser.parse_args()


def main() -> None:
    _ensure_src_on_path()
    
    from src.simulate import run_all_with_timelines
    from src.plots import (
        plot_all_scenarios_summary, 
        plot_comparison_all_scenarios,
        plot_all_scenarios_individual,
        plot_evolution_by_scenario,
        plot_evolution_comparison,
        plot_rentability_by_product,
        create_interactive_dashboard
    )

    args = parse_args()
    results = run_all_with_timelines(initial_value=args.initial)

    # Imprime resumo por cenário
    for scen_name, data in results.items():
        print(f"\n=== {scen_name} ===")
        print(data["summary"].to_string(index=False))

    # Salva resultados, se solicitado
    if args.save_results:
        os.makedirs(args.out_dir, exist_ok=True)
        
        # Cria planilha Excel com uma aba por título (produto)
        excel_path = os.path.join(args.out_dir, "simulacao_por_titulo.xlsx")
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Lista de produtos para criar as abas
            produtos = ["Tesouro_Prefixado", "Tesouro_IPCA_Plus", "Tesouro_Selic", "CDB_100_CDI", "LCI", "Poupanca"]
            
            # Uma aba por produto com todos os cenários
            for produto in produtos:
                sheet_name = produto.replace("_", " ")[:31]  # Excel limita a 31 caracteres
                
                # Combina dados de todos os cenários para este produto
                all_data = []
                
                # Adiciona timelines de todos os cenários para este produto
                for scen_name, data in results.items():
                    if produto in data["timelines"]:
                        timeline_df = data["timelines"][produto].copy()
                        timeline_df.insert(0, "CENARIO", scen_name)
                        # Substitui 'TIPO' por datas começando em 2025 (apenas data, sem hora)
                        dates = pd.date_range(start="2025-01-01", periods=len(timeline_df), freq='B').date
                        timeline_df.insert(0, "DATA", dates)
                        all_data.append(timeline_df)
                        
                        # Adiciona linha separadora entre cenários
                        if len(all_data) > 1:  # Se não for o primeiro cenário
                            separator_cols = ["DATA", "CENARIO"] + list(timeline_df.columns[2:])
                            separator_data = {col: ["---"] for col in separator_cols}
                            separator = pd.DataFrame(separator_data)
                            all_data.append(separator)
                
                # Combina tudo em uma única aba para este produto
                if all_data:
                    combined_data = pd.concat(all_data, ignore_index=True)
                    combined_data.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Adiciona aba de resumo com todos os cenários
            summary_data = []
            for scen_name, data in results.items():
                summary_df = data["summary"].copy()
                summary_df.insert(0, "CENARIO", scen_name)
                summary_data.append(summary_df)
            
            if summary_data:
                combined_summary = pd.concat(summary_data, ignore_index=True)
                combined_summary.to_excel(writer, sheet_name="Resumo", index=False)

        # print(f"\nPlanilha por título salva em: {os.path.abspath(excel_path)}")
        # print("Estrutura: 6 abas (uma por produto) com 3 cenários simulados em cada aba")
        # print("Cada aba contém: resumos dos 3 cenários + timelines diárias de 756 dias úteis")

    # Gera gráficos, se solicitado
    if args.save_figures or args.plotly or args.individual or args.evolucao or args.rentabilidade:
        os.makedirs(args.fig_dir, exist_ok=True)
        
        # Preparar dados para gráficos
        results_by_scenario = {name: data["summary"] for name, data in results.items()}
        
        if args.plotly or args.individual or args.evolucao or args.rentabilidade:
            # Gráficos Plotly interativos
            print("\n🎨 Gerando gráficos interativos com Plotly...")
            
            # Gráficos de evolução temporal
            if args.evolucao:
                evolution_figures = plot_evolution_by_scenario(
                    results,
                    save_dir=args.fig_dir,
                    show=False
                )
                print(f"📈 {len(evolution_figures)} gráficos de evolução criados (um por cenário)")
                
                # Gráfico comparativo de evolução
                plot_evolution_comparison(
                    results,
                    save_path=f"{args.fig_dir}/evolucao_comparativa.png",
                    show=False
                )
                print("📊 Gráfico comparativo de evolução criado")
            
            # Gráficos individuais por cenário
            if args.individual:
                individual_figures = plot_all_scenarios_individual(
                    results_by_scenario,
                    save_dir=args.fig_dir,
                    show=False
                )
                print(f"📈 {len(individual_figures)} gráficos individuais criados (um por cenário)")
            
            # Gráficos de rentabilidade por produto
            if args.rentabilidade:
                rentability_figures = plot_rentability_by_product(
                    results,  # Usar results completo com timelines
                    save_dir=args.fig_dir,
                    show=False
                )
                print(f"📊 {len(rentability_figures)} gráficos de evolução da rentabilidade criados (um por produto)")
            
            # Gráfico comparativo de todos os cenários
            if args.plotly and not args.individual and not args.evolucao:
                plot_comparison_all_scenarios(
                    results_by_scenario, 
                    save_path=f"{args.fig_dir}/comparacao_cenarios.png",
                    show=False
                )
            
            # Dashboard interativo
            if args.dashboard:
                create_interactive_dashboard(
                    results_by_scenario,
                    save_path=f"{args.fig_dir}/dashboard_interativo.html",
                    show=False
                )
                print(f"📊 Dashboard interativo salvo: {args.fig_dir}/dashboard_interativo.html")
            
            print(f"🎯 Gráficos Plotly salvos em: {os.path.abspath(args.fig_dir)}")
        else:
            # Gráficos tradicionais (Matplotlib)
            plot_all_scenarios_summary(results_by_scenario=results_by_scenario, save_dir=args.fig_dir, show=False)


if __name__ == "__main__":
    main()


