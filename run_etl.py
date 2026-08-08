from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DJANGO_ROOT = PROJECT_ROOT / "Celestial_ERP"


def run_step(name: str, command: list[str], cwd: Path) -> None:
    print(f"\n== {name} ==")
    print(" ".join(command))
    completed = subprocess.run(command, cwd=cwd, text=True)
    if completed.returncode != 0:
        raise SystemExit(f"Fallo el paso: {name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta el flujo ETL completo del ERP.")
    parser.add_argument("--input", type=Path, default=None, help="Archivo fuente .xlsx/.xls o CSV transformado.")
    parser.add_argument(
        "--source-format",
        choices=["auto", "historic_excel", "transformed_csv"],
        default="auto",
        help="Tipo de archivo fuente. Default: auto.",
    )
    parser.add_argument(
        "--transformed-output",
        type=Path,
        default=PROJECT_ROOT / "transformed.csv",
        help="Ruta del CSV transformado intermedio.",
    )
    parser.add_argument(
        "--category-output-dir",
        type=Path,
        default=PROJECT_ROOT / "csv_por_categoria",
        help="Carpeta de CSV por categoria.",
    )
    parser.add_argument(
        "--equivalent-output-dir",
        type=Path,
        default=PROJECT_ROOT / "csv_equivalentes_liquidaciones",
        help="Carpeta de CSV equivalentes a plantilla.",
    )
    parser.add_argument(
        "--excel-output",
        type=Path,
        default=PROJECT_ROOT / "Liquidaciones_Historicas_Cargadas.xlsx",
        help="Archivo Excel final generado.",
    )
    parser.add_argument("--rut-empresa", default="", help="Rut empresa para archivos de liquidaciones.")
    parser.add_argument("--skip-excel", action="store_true", help="No genera el Excel final.")
    parser.add_argument("--skip-import", action="store_true", help="No importa datos al ERP Django.")
    parser.add_argument("--clear", action="store_true", help="Borra datos previos antes de importar.")
    return parser.parse_args()


def source_format(path: Path | None, requested: str) -> str:
    if requested != "auto":
        return requested
    if path is None:
        return "historic_excel"
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return "historic_excel"
    if suffix == ".csv":
        return "transformed_csv"
    raise SystemExit(f"Formato no soportado: {suffix}")


def main() -> None:
    args = parse_args()
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Inicio ETL: {started_at}")

    input_path = args.input or PROJECT_ROOT / "ITEMS_ACUMULADOS_Historico Payroll.xlsx"
    transformed_path = args.transformed_output
    detected_format = source_format(input_path, args.source_format)

    if detected_format == "historic_excel":
        run_step(
            "Transformar historico",
            [sys.executable, "dataload.py", "--input", str(input_path), "--output", str(transformed_path)],
            PROJECT_ROOT,
        )
    else:
        transformed_path = input_path
        print(f"CSV transformado recibido: {transformed_path}")

    run_step(
        "Separar por categoria",
        [sys.executable, "tabcreated.py", "--input", str(transformed_path), "--output-dir", str(args.category_output_dir)],
        PROJECT_ROOT,
    )
    run_step(
        "Generar CSV equivalentes",
        [
            sys.executable,
            "build_liquidaciones_csvs.py",
            "--input",
            str(transformed_path),
            "--output-dir",
            str(args.equivalent_output_dir),
            "--rut-empresa",
            args.rut_empresa,
        ],
        PROJECT_ROOT,
    )

    if not args.skip_excel:
        run_step(
            "Generar Excel final",
            [
                sys.executable,
                "transfer_liquidaciones_to_excel.py",
                "--input-dir",
                str(args.equivalent_output_dir),
                "--output",
                str(args.excel_output),
            ],
            PROJECT_ROOT,
        )

    if not args.skip_import:
        import_command = [
            sys.executable,
            "manage.py",
            "import_payroll_data",
            "--transformed",
            str(transformed_path),
            "--summaries",
            str(args.equivalent_output_dir / "Liquidaciones.csv"),
        ]
        if args.clear:
            import_command.append("--clear")
        run_step("Importar al ERP", import_command, DJANGO_ROOT)

    print("\nETL completado.")


if __name__ == "__main__":
    main()
