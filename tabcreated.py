from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path("transformed.csv")
DEFAULT_OUTPUT_DIR = Path("csv_por_categoria")
CATEGORY_COLUMN = "categoria_item"
CSV_SEPARATOR = ";"


def safe_filename(value: object) -> str:
    text = "sin_categoria" if pd.isna(value) else str(value).strip()
    if not text:
        text = "sin_categoria"

    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", ascii_text).strip("._-")
    return safe or "sin_categoria"


def split_by_category(input_path: Path, output_dir: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(f"No existe el archivo de entrada: {input_path}")

    df = pd.read_csv(input_path, sep=CSV_SEPARATOR, dtype=str, encoding="utf-8-sig")
    if CATEGORY_COLUMN not in df.columns:
        raise ValueError(f"Falta la columna requerida: {CATEGORY_COLUMN}")

    output_dir.mkdir(parents=True, exist_ok=True)
    for old_csv in output_dir.glob("*.csv"):
        old_csv.unlink()

    summary_rows = []
    for category, category_df in df.groupby(CATEGORY_COLUMN, dropna=False, sort=True):
        filename = f"{safe_filename(category)}.csv"
        output_path = output_dir / filename

        category_df.to_csv(
            output_path,
            sep=CSV_SEPARATOR,
            index=False,
            encoding="utf-8-sig",
        )

        summary_rows.append(
            {
                "categoria_item": "sin_categoria" if pd.isna(category) else category,
                "archivo": str(output_path),
                "filas": len(category_df),
            }
        )

    return pd.DataFrame(summary_rows).sort_values("categoria_item", kind="stable")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Separa transformed.csv en un CSV por cada categoria_item."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"CSV transformado de entrada. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Carpeta donde se guardan los CSV por categoria. Default: {DEFAULT_OUTPUT_DIR}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = split_by_category(args.input, args.output_dir)

    print(f"Carpeta generada: {args.output_dir}")
    print(f"Archivos generados: {len(summary)}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
