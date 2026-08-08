from __future__ import annotations

import argparse
from pathlib import Path

import openpyxl
import pandas as pd


DEFAULT_INPUT = Path("transformed.csv")
DEFAULT_TEMPLATE = Path("Copia de Liquidaciones Históricas (37).xlsx")
DEFAULT_OUTPUT_DIR = Path("csv_equivalentes_liquidaciones")
DEFAULT_DESCRIPTIONS_DIR = Path("descripciones_codigo_item")
CSV_SEPARATOR = ";"

KEY_COLUMNS = ["periodo", "codigo"]

SHEET_NAMES = {
    "liquidaciones": "Liquidaciones",
    "haberes_imponibles": "Haberes Imponibles",
    "haberes_no_imponibles": "Haberes No Imponibles",
    "descuentos": "Descuentos",
    "finiquito": "Líneas de Finiquito",
}

HABERES_IMPONIBLES = {"haberes_normales_imponibles"}
HABERES_NO_IMPONIBLES = {"haberes_exentos_no_imponibles", "asignaciones_familiares"}
DESCUENTOS = {"descuentos_legales_previsionales", "otros_descuentos"}

AFP_CODES = {"AFPCOT", "AFPREL", "AFPRLQ"}
SALUD_CODES = {"ISAPRE1", "ISAREL", "ISARLQ"}
IMPUESTO_CODES = {"IMPUES", "IMPREL", "IMPRLQ"}
PREVISION_VOLUNTARIA_CODES = {"AFPAHO", "AHOPRE", "AHOVOL", "APVEXE"}
CESANTIA_TRABAJADOR_CODES = {"SEGCET", "SCTREL", "SCTRLQ"}
CESANTIA_EMPLEADOR_CODES = {"SEGCEE", "SCEREL", "SCERLQ"}
MUTUAL_CODES = {"MUTUAL", "MUTREL"}
SIS_CODES = {"SISAFP", "SISREL", "SISRLQ"}
LEY_SANNA_CODES = {"LSANNA", "LSAREL", "LSARLQ"}
AFP_EMPLEADOR_CODES = {"COCAPI"}
EXPECTATIVA_VIDA_CODES = {"COSESO"}


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def document_number(periodo: object, codigo: object) -> str:
    return f"{clean_text(periodo)}-{clean_text(codigo)}"


def read_template_headers(template_path: Path) -> dict[str, list[str]]:
    workbook = openpyxl.load_workbook(template_path, read_only=True, data_only=False)
    headers = {}
    for sheet_name in SHEET_NAMES.values():
        worksheet = workbook[sheet_name]
        first_row = next(worksheet.iter_rows(min_row=1, max_row=1, values_only=True))
        headers[sheet_name] = [clean_text(value) for value in first_row if clean_text(value)]
    return headers


def read_transformed(input_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path, sep=CSV_SEPARATOR, dtype=str, encoding="utf-8-sig")
    required = {
        "periodo",
        "codigo",
        "Rut",
        "nombre",
        "diastr",
        "codigo_item",
        "categoria_item",
        "monto",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Faltan columnas en {input_path}: {', '.join(missing)}")

    df["periodo"] = df["periodo"].map(clean_text)
    df["codigo"] = df["codigo"].map(clean_text)
    df["Rut"] = df["Rut"].map(clean_text)
    df["nombre"] = df["nombre"].map(clean_text)
    df["codigo_item"] = df["codigo_item"].map(clean_text)
    df["categoria_item"] = df["categoria_item"].map(clean_text)
    df["monto_num"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0).round().astype("int64")
    df["documento"] = [document_number(row.periodo, row.codigo) for row in df.itertuples()]
    return df


def read_descriptions(descriptions_dir: Path) -> dict[str, str]:
    if not descriptions_dir.exists():
        return {}

    descriptions = {}
    for path in sorted(descriptions_dir.glob("*_descripciones.csv")):
        if path.name == "todos_los_codigo_item_descripciones.csv":
            continue

        df = pd.read_csv(path, sep=CSV_SEPARATOR, dtype=str, encoding="utf-8-sig").fillna("")
        if not {"codigo_item", "descripcion"}.issubset(df.columns):
            continue

        for row in df.itertuples(index=False):
            code = clean_text(row.codigo_item)
            description = clean_text(row.descripcion)
            if code and description:
                descriptions[code] = description

    # The historic file keeps a couple of source suffixes that the description files normalize.
    aliases = {
        "DIASTR1": "DIASTR",
        "ISAPRE1": "ISAPRE",
    }
    for source_code, description_code in aliases.items():
        if source_code not in descriptions and description_code in descriptions:
            descriptions[source_code] = descriptions[description_code]

    return descriptions


def grouped_sum(df: pd.DataFrame, mask: pd.Series) -> pd.Series:
    return df.loc[mask].groupby(KEY_COLUMNS)["monto_num"].sum()


def value_from_series(base: pd.DataFrame, series: pd.Series) -> pd.Series:
    index = pd.MultiIndex.from_frame(base[KEY_COLUMNS])
    return pd.Series(series.reindex(index, fill_value=0).to_numpy(), index=base.index)


def build_line_sheet(
    df: pd.DataFrame,
    categories: set[str],
    headers: list[str],
    rut_empresa: str,
    descriptions: dict[str, str],
    tributable: str | None = None,
) -> pd.DataFrame:
    filtered = df[df["categoria_item"].isin(categories)].copy()
    item_names = filtered["codigo_item"].map(descriptions).fillna(filtered["codigo_item"])

    output = pd.DataFrame(
        {
            "Número de Documento*": filtered["documento"],
            "Código de Ficha": filtered["codigo"],
            "Rut empresa": rut_empresa,
            "Nombre": item_names,
            "Monto": filtered["monto_num"],
        }
    )
    if "Tributable" in headers:
        output["Tributable"] = tributable or "No"
    if "Codigo item" in headers:
        output["Codigo item"] = filtered["codigo_item"]
    return output.reindex(columns=headers)


def build_liquidaciones(df: pd.DataFrame, headers: list[str], rut_empresa: str) -> pd.DataFrame:
    base = (
        df.sort_values(KEY_COLUMNS)
        .groupby(KEY_COLUMNS, as_index=False)
        .agg(
            documento=("documento", "first"),
            diastr=("diastr", "first"),
        )
    )

    category = df["categoria_item"]
    code = df["codigo_item"]

    total_haberes_imponibles = value_from_series(
        base, grouped_sum(df, category.isin(HABERES_IMPONIBLES))
    )
    total_haberes_no_imponibles = value_from_series(
        base, grouped_sum(df, category.isin(HABERES_NO_IMPONIBLES))
    )
    total_descuentos_legales = value_from_series(
        base, grouped_sum(df, category.eq("descuentos_legales_previsionales"))
    )
    total_otros_descuentos = value_from_series(
        base, grouped_sum(df, category.eq("otros_descuentos"))
    )
    total_contribucion_empleador = value_from_series(
        base, grouped_sum(df, category.eq("contribucion_empleador"))
    )
    total_provisiones = value_from_series(
        base, grouped_sum(df, category.eq("provisiones"))
    )
    sueldo_liquido_fuente = value_from_series(base, grouped_sum(df, code.eq("A000")))

    impuesto = value_from_series(base, grouped_sum(df, code.isin(IMPUESTO_CODES)))
    pago_prevision = value_from_series(base, grouped_sum(df, code.isin(AFP_CODES)))
    pago_salud = value_from_series(base, grouped_sum(df, code.isin(SALUD_CODES)))
    pago_prevision_voluntaria = value_from_series(
        base, grouped_sum(df, code.isin(PREVISION_VOLUNTARIA_CODES))
    )
    cesantia_trabajador = value_from_series(
        base, grouped_sum(df, code.isin(CESANTIA_TRABAJADOR_CODES))
    )
    cesantia_empleador = value_from_series(
        base, grouped_sum(df, code.isin(CESANTIA_EMPLEADOR_CODES))
    )
    mutual = value_from_series(base, grouped_sum(df, code.isin(MUTUAL_CODES)))
    sis = value_from_series(base, grouped_sum(df, code.isin(SIS_CODES)))
    ley_sanna = value_from_series(base, grouped_sum(df, code.isin(LEY_SANNA_CODES)))
    afp_empleador = value_from_series(base, grouped_sum(df, code.isin(AFP_EMPLEADOR_CODES)))
    expectativa_vida = value_from_series(base, grouped_sum(df, code.isin(EXPECTATIVA_VIDA_CODES)))
    sueldo_base = value_from_series(base, grouped_sum(df, code.eq("SUBASE")))
    aportes_asignados = cesantia_empleador + mutual + sis + ley_sanna + afp_empleador + expectativa_vida
    otros_aportes_patronales = total_contribucion_empleador - aportes_asignados

    costo_empresa = (
        total_haberes_imponibles
        + total_haberes_no_imponibles
        + total_contribucion_empleador
        + total_provisiones
    )

    output = pd.DataFrame(
        {
            "Número de Documento*": base["documento"],
            "Código de Ficha": base["codigo"],
            "RUT Empresa*": rut_empresa,
            "Sueldo Base*": sueldo_base,
            "Días Laborales*": 0,
            "Días Trabajados*": pd.to_numeric(base["diastr"], errors="coerce").fillna(0).astype("int64"),
            "Días Licencias*": 0,
            "Días Permisos*": 0,
            "Días Ausencias*": 0,
            "Días Suspendidos*": 0,
            "Número Horas No Trabajadas*": 0,
            "Sobretiempo horas extras*": 0,
            "Costo Empresa*": costo_empresa,
            "Total Haberes Imponibles*": total_haberes_imponibles,
            "Total Haberes No Imponibles No Tributables*": total_haberes_no_imponibles,
            "Total Haberes No Imponibles Tributables*": 0,
            "Total Descuentos Legales*": total_descuentos_legales,
            "Total Otros Descuentos*": total_otros_descuentos,
            "Sueldo Líquido*": sueldo_liquido_fuente,
            "Base Tributable*": total_haberes_imponibles,
            "Rebaja Zona Extrema*": 0,
            "Impuesto*": impuesto,
            "Pago Previsión*": pago_prevision,
            "Pago Salud Obligatoria*": pago_salud,
            "Pago Salud Voluntaria*": 0,
            "Pago Previsión Voluntaria*": pago_prevision_voluntaria,
            "Seguro Cesantía (Trabajador)*": cesantia_trabajador,
            "Trabajo Pesado (Trabajador)*": 0,
            "Seguro Cesantia (Empleador)": cesantia_empleador,
            "Mutual Empleador": mutual,
            "Pago SIS (Empleador)": sis,
            "Trabajo Pesado (Empleador)": 0,
            "AFP prevision empleador": afp_empleador,
            "Cotización Expectativa de Vida": expectativa_vida,
            "Previsión (Ley protección empleo)": 0,
            "Salud Obligatoria (Ley protección empleo)": 0,
            "Salud Voluntaria (Ley protección empleo)": 0,
            "Seguro Cesantía Trabajador (Ley protección empleo)": 0,
            "Seguro Cesantía Empleador (Ley protección empleo)": 0,
            "Ley Sanna (Ley protección empleo)": ley_sanna,
            "Trabajo Pesado Trabajador (Ley protección empleo)": 0,
            "Trabajo Pesado Empleador (Ley protección empleo)": 0,
            "SIS (Ley protección empleo)": 0,
            "Otros Aportes Patronales": otros_aportes_patronales,
            "Saldo Sobregiro*": 0,
        }
    )
    return output.reindex(columns=headers)


def write_outputs(
    sheets: dict[str, pd.DataFrame],
    output_dir: Path,
) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_rows = []

    for sheet_name, sheet_df in sheets.items():
        filename = f"{sheet_name}.csv".replace(" ", "_")
        output_path = output_dir / filename
        sheet_df.to_csv(output_path, sep=CSV_SEPARATOR, index=False, encoding="utf-8-sig")
        amount_column = "Monto" if "Monto" in sheet_df.columns else None
        total = int(pd.to_numeric(sheet_df[amount_column], errors="coerce").fillna(0).sum()) if amount_column else 0
        summary_rows.append(
            {
                "hoja": sheet_name,
                "archivo": str(output_path),
                "filas": len(sheet_df),
                "total_monto_lineas": total,
            }
        )

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(output_dir / "resumen_generacion.csv", sep=CSV_SEPARATOR, index=False, encoding="utf-8-sig")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera CSV equivalentes a las hojas de la plantilla de liquidaciones."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"CSV transformado de entrada. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "-t",
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help=f"Excel plantilla. Default: {DEFAULT_TEMPLATE}",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Carpeta de salida. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--rut-empresa",
        default="",
        help="Rut empresa que se escribira en las hojas generadas.",
    )
    parser.add_argument(
        "--descriptions-dir",
        type=Path,
        default=DEFAULT_DESCRIPTIONS_DIR,
        help=f"Carpeta con descripciones de codigo_item. Default: {DEFAULT_DESCRIPTIONS_DIR}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    headers = read_template_headers(args.template)
    df = read_transformed(args.input)
    descriptions = read_descriptions(args.descriptions_dir)

    sheets = {
        SHEET_NAMES["liquidaciones"]: build_liquidaciones(
            df,
            headers[SHEET_NAMES["liquidaciones"]],
            args.rut_empresa,
        ),
        SHEET_NAMES["haberes_imponibles"]: build_line_sheet(
            df,
            HABERES_IMPONIBLES,
            headers[SHEET_NAMES["haberes_imponibles"]],
            args.rut_empresa,
            descriptions,
        ),
        SHEET_NAMES["haberes_no_imponibles"]: build_line_sheet(
            df,
            HABERES_NO_IMPONIBLES,
            headers[SHEET_NAMES["haberes_no_imponibles"]],
            args.rut_empresa,
            descriptions,
            tributable="No",
        ),
        SHEET_NAMES["descuentos"]: build_line_sheet(
            df,
            DESCUENTOS,
            headers[SHEET_NAMES["descuentos"]],
            args.rut_empresa,
            descriptions,
        ),
        SHEET_NAMES["finiquito"]: pd.DataFrame(columns=headers[SHEET_NAMES["finiquito"]]),
    }

    summary = write_outputs(sheets, args.output_dir)
    print(f"Carpeta generada: {args.output_dir}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
