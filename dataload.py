from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path("ITEMS_ACUMULADOS_Historico Payroll.xlsx")
DEFAULT_OUTPUT = Path("transformed.csv")
SOURCE_SHEET = "Sheet1"

IDENTITY_COLUMNS = [
    "codigo",
    "nombre",
    "Codigo A.F.P.",
    "Isapre",
    "diastr",
    "Division",
    "Fecha de Ingreso",
    "Fecha de Retiro",
    "Horario de trabajo",
    "Jornada: V / S",
    "Jornada de contrato",
    "Rut",
    "periodo",
]

ITEM_CATEGORIES = {
    "000011": "haberes_exentos_no_imponibles",
    "11": "haberes_exentos_no_imponibles",
    "A000": "haberes_exentos_no_imponibles",
    "AS1COL": "haberes_exentos_no_imponibles",
    "ASICOL": "haberes_exentos_no_imponibles",
    "ASIMOV": "haberes_exentos_no_imponibles",
    "BIASUG": "haberes_exentos_no_imponibles",
    "BOASIG": "haberes_exentos_no_imponibles",
    "FOTROS": "haberes_exentos_no_imponibles",
    "INDLEA": "haberes_exentos_no_imponibles",
    "INDLEG": "haberes_exentos_no_imponibles",
    "INDVOL": "haberes_exentos_no_imponibles",
    "MESDEA": "haberes_exentos_no_imponibles",
    "OTSBNI": "haberes_exentos_no_imponibles",
    "PERDID": "haberes_exentos_no_imponibles",
    "SBGIRO": "haberes_exentos_no_imponibles",
    "TRAGEN": "haberes_exentos_no_imponibles",
    "TRAREM": "haberes_exentos_no_imponibles",
    "TRESPH": "haberes_exentos_no_imponibles",
    "VACPRO": "haberes_exentos_no_imponibles",
    "VIATIC": "haberes_exentos_no_imponibles",
    "AGUCIA": "haberes_normales_imponibles",
    "AGUINA": "haberes_normales_imponibles",
    "ATRASO": "haberes_normales_imponibles",
    "BASELI": "haberes_normales_imponibles",
    "BODESE": "haberes_normales_imponibles",
    "BESPE": "haberes_normales_imponibles",
    "BOESPE": "haberes_normales_imponibles",
    "BONCIA": "haberes_normales_imponibles",
    "BONCOM": "haberes_normales_imponibles",
    "BONCON": "haberes_normales_imponibles",
    "BONDEF": "haberes_normales_imponibles",
    "BONESC": "haberes_normales_imponibles",
    "BONESP": "haberes_normales_imponibles",
    "BONOCE": "haberes_normales_imponibles",
    "BONQUI": "haberes_normales_imponibles",
    "BONRET": "haberes_normales_imponibles",
    "BONVAC": "haberes_normales_imponibles",
    "DIAPEN": "haberes_normales_imponibles",
    "DIASFA": "haberes_normales_imponibles",
    "DIASLI": "haberes_normales_imponibles",
    "DIASTR": "haberes_normales_imponibles",
    "DIASTR1": "haberes_normales_imponibles",
    "DIFBVA": "haberes_normales_imponibles",
    "DIFSUE": "haberes_normales_imponibles",
    "HEX050": "haberes_normales_imponibles",
    "HEX100": "haberes_normales_imponibles",
    "HRSEXT": "haberes_normales_imponibles",
    "OTSBON": "haberes_normales_imponibles",
    "TRESPD": "haberes_normales_imponibles",
    "VACCIA": "haberes_normales_imponibles",
    "SUBASE": "haberes_normales_imponibles",
    "ASIFAM": "asignaciones_familiares",
    "ASIFAP": "asignaciones_familiares",
    "ASIFAR": "asignaciones_familiares",
    "COCAPI": "contribucion_empleador",
    "COCREL": "contribucion_empleador",
    "COCRLQ": "contribucion_empleador",
    "COSESO": "contribucion_empleador",
    "COSREL": "contribucion_empleador",
    "COSRLQ": "contribucion_empleador",
    "LSANNA": "contribucion_empleador",
    "LSAREL": "contribucion_empleador",
    "LSARLQ": "contribucion_empleador",
    "MUTREL": "contribucion_empleador",
    "MUTUAL": "contribucion_empleador",
    "RIMALM": "contribucion_empleador",
    "SCEREL": "contribucion_empleador",
    "SCERLQ": "contribucion_empleador",
    "SCIREL": "contribucion_empleador",
    "SCIRLQ": "contribucion_empleador",
    "SEGCEE": "contribucion_empleador",
    "SEGCEI": "contribucion_empleador",
    "SISAFP": "contribucion_empleador",
    "SISREL": "contribucion_empleador",
    "SISRLQ": "contribucion_empleador",
    "CAJACO": "contribucion_empleador",
    "PROACU": "provisiones",
    "POCON": "provisiones",
    "PROCON": "provisiones",
    "PROGAN": "provisiones",
    "PROIAS": "provisiones",
    "PROVAC": "provisiones",
    "AFIAHO": "descuentos_legales_previsionales",
    "AFIVOL": "descuentos_legales_previsionales",
    "AFPADI": "descuentos_legales_previsionales",
    "AFPAH2": "descuentos_legales_previsionales",
    "AFPAHO": "descuentos_legales_previsionales",
    "AFPCOT": "descuentos_legales_previsionales",
    "AFPISU": "descuentos_legales_previsionales",
    "AFPREL": "descuentos_legales_previsionales",
    "AFPRLQ": "descuentos_legales_previsionales",
    "AFPTOP": "descuentos_legales_previsionales",
    "AHOPRE": "descuentos_legales_previsionales",
    "AHOVOL": "descuentos_legales_previsionales",
    "APVEXE": "descuentos_legales_previsionales",
    "DIFCOT": "descuentos_legales_previsionales",
    "IMPREL": "descuentos_legales_previsionales",
    "IMPRLQ": "descuentos_legales_previsionales",
    "IMPUES": "descuentos_legales_previsionales",
    "ISAPRE": "descuentos_legales_previsionales",
    "ISAREL": "descuentos_legales_previsionales",
    "ISARLQ": "descuentos_legales_previsionales",
    "ISAPRE1": "descuentos_legales_previsionales",
    "PRESS3": "descuentos_legales_previsionales",
    "SCTREL": "descuentos_legales_previsionales",
    "SCTRLQ": "descuentos_legales_previsionales",
    "SEGCET": "descuentos_legales_previsionales",
    "AHCAJA": "otros_descuentos",
    "AHOPER": "otros_descuentos",
    "ANTAGI": "otros_descuentos",
    "ANTBEN": "otros_descuentos",
    "ANTBES": "otros_descuentos",
    "ANTBON": "otros_descuentos",
    "ANTCIA": "otros_descuentos",
    "ANTDIF": "otros_descuentos",
    "ANTFIN": "otros_descuentos",
    "ANTICA": "otros_descuentos",
    "ANTICI": "otros_descuentos",
    "ANTQUI": "otros_descuentos",
    "ANTVIA": "otros_descuentos",
    "ANTVAC": "otros_descuentos",
    "DESAJU": "otros_descuentos",
    "DESCCO": "otros_descuentos",
    "DESCHI": "otros_descuentos",
    "DESCHU": "otros_descuentos",
    "DESCOL": "otros_descuentos",
    "DESFAL": "otros_descuentos",
    "DESFAR": "otros_descuentos",
    "DESGIM": "otros_descuentos",
    "DESOP": "otros_descuentos",
    "DESOPT": "otros_descuentos",
    "DESQUI": "otros_descuentos",
    "DESSEC": "otros_descuentos",
    "DESUES": "otros_descuentos",
    "DEUFIN": "otros_descuentos",
    "OTDESC": "otros_descuentos",
    "OTRANT": "otros_descuentos",
    "PRCAJ2": "otros_descuentos",
    "PRECA3": "otros_descuentos",
    "PRECA4": "otros_descuentos",
    "PRECAJ": "otros_descuentos",
    "PRECIA": "otros_descuentos",
    "PREEMP": "otros_descuentos",
    "PRHERO": "otros_descuentos",
    "REDONA": "otros_descuentos",
    "RETJUD": "otros_descuentos",
    "SBGIRA": "otros_descuentos",
    "SEGCA1": "otros_descuentos",
    "SEGMUT": "otros_descuentos",
    "SUMCAJ": "otros_descuentos",
    "SUMSEG": "otros_descuentos",
    "Totales": "totales",
}

REQUIRES_CONFIRMATION = {
    "000011",
    "AGUCIA",
    "ANTAGI",
    "ANTBEN",
    "ANTBES",
    "ANTBON",
    "ANTCIA",
    "ANTDIF",
    "ANTFIN",
    "ANTICA",
    "ANTVIA",
    "BOASIG",
    "FOTROS",
    "MESDEA",
    "RIMALM",
    "SEGCA1",
    "SUMSEG",
    "TRAGEN",
    "TRESPD",
    "TRESPH",
    "VACPRO",
}


def canonical_item_code(column: object) -> str:
    return str(column).strip()


def read_historic_payroll(input_path: Path) -> pd.DataFrame:
    return pd.read_excel(input_path, sheet_name=SOURCE_SHEET, dtype=str)


def transform_payroll(df: pd.DataFrame) -> pd.DataFrame:
    missing_identity = [column for column in IDENTITY_COLUMNS if column not in df.columns]
    if missing_identity:
        raise ValueError(f"Faltan columnas base en el Excel: {', '.join(missing_identity)}")

    source_item_columns = [
        column
        for column in df.columns
        if column not in IDENTITY_COLUMNS
    ]

    renamed_items = {
        column: canonical_item_code(column)
        for column in source_item_columns
    }

    normalized = df.rename(columns=renamed_items)
    item_columns = [renamed_items[column] for column in source_item_columns]

    transformed = normalized.melt(
        id_vars=IDENTITY_COLUMNS,
        value_vars=item_columns,
        var_name="codigo_item",
        value_name="monto",
    )

    transformed["monto"] = pd.to_numeric(transformed["monto"], errors="coerce").fillna(0)
    transformed = transformed[transformed["monto"] != 0].copy()
    transformed["monto"] = transformed["monto"].round().astype("Int64")
    transformed["categoria_item"] = transformed["codigo_item"].map(ITEM_CATEGORIES)
    transformed["requiere_confirmacion"] = transformed["codigo_item"].isin(REQUIRES_CONFIRMATION)
    transformed["categoria_item"] = transformed["categoria_item"].fillna("sin_clasificar")

    ordered_columns = [
        "periodo",
        "codigo",
        "Rut",
        "nombre",
        "Division",
        "Codigo A.F.P.",
        "Isapre",
        "diastr",
        "Fecha de Ingreso",
        "Fecha de Retiro",
        "Horario de trabajo",
        "Jornada: V / S",
        "Jornada de contrato",
        "codigo_item",
        "categoria_item",
        "requiere_confirmacion",
        "monto",
    ]
    return transformed[ordered_columns].sort_values(
        ["periodo", "codigo", "categoria_item", "codigo_item"],
        kind="stable",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transforma el historico payroll acumulado a un CSV largo clasificado."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Excel historico de origen. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"CSV de salida. Default: {DEFAULT_OUTPUT}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.input.exists():
        raise SystemExit(f"No existe el archivo de entrada: {args.input}")

    source = read_historic_payroll(args.input)
    transformed = transform_payroll(source)
    transformed.to_csv(args.output, sep=";", index=False, encoding="utf-8-sig")

    by_category = transformed.groupby("categoria_item", dropna=False)["monto"].agg(
        filas="count",
        total="sum",
    )

    print(f"Archivo generado: {args.output}")
    print(f"Filas exportadas: {len(transformed)}")
    print(by_category.to_string())


if __name__ == "__main__":
    main()
