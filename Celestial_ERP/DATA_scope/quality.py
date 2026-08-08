from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


REQUIRED_TRANSFORMED_COLUMNS = {
    "periodo",
    "codigo",
    "Rut",
    "nombre",
    "codigo_item",
    "categoria_item",
    "monto",
}


@dataclass
class QualityIssue:
    severity: str
    row_number: int
    field: str
    message: str


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def is_decimal(value: str) -> bool:
    if not value:
        return False
    try:
        Decimal(value.replace(",", "."))
    except InvalidOperation:
        return False
    return True


def validate_transformed_csv(path: Path) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    seen_keys: set[tuple[str, str, str]] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        headers = set(reader.fieldnames or [])
        for missing in sorted(REQUIRED_TRANSFORMED_COLUMNS - headers):
            issues.append(QualityIssue("error", 0, missing, "Columna requerida ausente."))
        if issues:
            return issues

        for row_number, row in enumerate(reader, start=2):
            periodo = clean(row.get("periodo"))
            codigo = clean(row.get("codigo"))
            codigo_item = clean(row.get("codigo_item"))
            monto = clean(row.get("monto"))

            for field in ["periodo", "codigo", "nombre", "codigo_item", "categoria_item"]:
                if not clean(row.get(field)):
                    issues.append(QualityIssue("error", row_number, field, "Valor obligatorio vacio."))
            if periodo and (len(periodo) != 6 or not periodo.isdigit()):
                issues.append(QualityIssue("error", row_number, "periodo", "Periodo debe usar formato AAAAMM."))
            if not is_decimal(monto):
                issues.append(QualityIssue("error", row_number, "monto", "Monto no numerico."))

            key = (periodo, codigo, codigo_item)
            if all(key):
                if key in seen_keys:
                    issues.append(QualityIssue("warning", row_number, "periodo/codigo/codigo_item", "Movimiento duplicado en archivo."))
                seen_keys.add(key)
    return issues


def write_quality_report(path: Path, issues: list[QualityIssue]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["severity", "row_number", "field", "message"])
        for issue in issues:
            writer.writerow([issue.severity, issue.row_number, issue.field, issue.message])
