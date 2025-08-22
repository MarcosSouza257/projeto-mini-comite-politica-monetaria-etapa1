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
    parser.add_argument("--save-results", action="store_true", help="Salvar resumos em CSV (pasta data/)")
    parser.add_argument("--out-dir", type=str, default="data", help="Diretório para salvar resultados")
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

    # Salva resultados, se solicitado
    if args.save_results:
        os.makedirs(args.out_dir, exist_ok=True)
        combined_rows = []
        for scen_name, df in results.items():
            slug = scen_name.replace(" ", "_").lower()
            out_path = os.path.join(args.out_dir, f"{slug}_summary.csv")
            df.to_csv(out_path, index=False, encoding="utf-8")
            # acumula para CSV combinado
            tmp = df.copy()
            tmp.insert(0, "cenario", scen_name)
            combined_rows.append(tmp)
        combined = combined_rows[0].append(combined_rows[1:], ignore_index=True) if combined_rows else None
        if combined is not None:
            combined.to_csv(os.path.join(args.out_dir, "resumo_todos_os_cenarios.csv"), index=False, encoding="utf-8")
        print(f"\nResultados salvos em: {os.path.abspath(args.out_dir)}")

    # Gera gráficos, se solicitado
    if args.save_figures:
        os.makedirs(args.fig_dir, exist_ok=True)
        plot_all_scenarios_summary(results_by_scenario=results, save_dir=args.fig_dir, show=True)
        print(f"\nGráficos salvos em: {os.path.abspath(args.fig_dir)}")


if __name__ == "__main__":
    main()


