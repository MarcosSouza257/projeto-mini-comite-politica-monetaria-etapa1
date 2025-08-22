from __future__ import annotations

import argparse
import os
import sys


def _ensure_src_on_path() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(here, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa simulações dos cenários e produtos.")
    parser.add_argument("--initial", type=float, default=100_000.0, help="Valor inicial (R$)")
    parser.add_argument("--save-figures", action="store_true", help="Salvar gráficos em figures/")
    parser.add_argument("--fig-dir", type=str, default="figures", help="Diretório para salvar gráficos")
    return parser.parse_args()


def main() -> None:
    _ensure_src_on_path()

    from simulate import run_all
    from plots import plot_all_scenarios_summary

    args = parse_args()
    results = run_all(initial_value=args.initial)

    # Imprime resumo por cenário
    for scen_name, df in results.items():
        print(f"\n=== {scen_name} ===")
        print(df.to_string(index=False))

    # Gera gráficos, se solicitado
    if args.save_figures:
        os.makedirs(args.fig_dir, exist_ok=True)
        plot_all_scenarios_summary(results_by_scenario=results, save_dir=args.fig_dir, show=False)
        print(f"\nGráficos salvos em: {os.path.abspath(args.fig_dir)}")


if __name__ == "__main__":
    main()


