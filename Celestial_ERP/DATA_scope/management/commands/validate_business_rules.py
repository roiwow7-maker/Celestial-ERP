from __future__ import annotations

import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from DATA_scope.models import PayrollEntry, PayrollItem, PayrollSummary


SUMMARY_FIELD_TO_CATEGORIES = {
    "total_haberes_imponibles": [PayrollItem.CATEGORY_HABERES_IMPONIBLES],
    "total_haberes_no_imponibles": [
        PayrollItem.CATEGORY_HABERES_EXENTOS,
        PayrollItem.CATEGORY_ASIGNACIONES,
    ],
    "total_descuentos_legales": [PayrollItem.CATEGORY_DESCUENTOS_LEGALES],
    "total_otros_descuentos": [PayrollItem.CATEGORY_OTROS_DESCUENTOS],
}
SOURCE_CODE_TO_SUMMARY_FIELD = {
    "A000": "sueldo_liquido",
}


class Command(BaseCommand):
    help = "Valida reglas de negocio basicas comparando resumenes con movimientos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=Path,
            default=settings.PROJECT_ROOT / "reports" / "business_rules_validation.csv",
            help="CSV de salida con diferencias detectadas.",
        )
        parser.add_argument("--fail-on-mismatch", action="store_true", help="Retorna error si hay diferencias.")

    def handle(self, *args, **options):
        output: Path = options["output"]
        output.parent.mkdir(parents=True, exist_ok=True)

        sums = defaultdict(lambda: defaultdict(Decimal))
        validated_categories = {
            category
            for categories in SUMMARY_FIELD_TO_CATEGORIES.values()
            for category in categories
        }

        for entry in PayrollEntry.objects.select_related("item").filter(item__categoria__in=validated_categories):
            key = (entry.period_id, entry.employee_id)
            sums[key][entry.item.categoria] += entry.monto

        source_code_sums = defaultdict(lambda: defaultdict(Decimal))
        for entry in PayrollEntry.objects.select_related("item").filter(item__codigo__in=SOURCE_CODE_TO_SUMMARY_FIELD.keys()):
            key = (entry.period_id, entry.employee_id)
            source_code_sums[key][entry.item.codigo] += entry.monto

        mismatch_count = 0
        checked_count = 0
        with output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(["periodo", "codigo_ficha", "campo", "resumen", "movimientos", "diferencia"])
            for summary in PayrollSummary.objects.select_related("period", "employee").all():
                checked_count += 1
                key = (summary.period_id, summary.employee_id)
                for field_name, categories in SUMMARY_FIELD_TO_CATEGORIES.items():
                    expected = getattr(summary, field_name) or Decimal("0")
                    actual = sum((sums[key].get(category, Decimal("0")) for category in categories), Decimal("0"))
                    difference = expected - actual
                    if difference:
                        mismatch_count += 1
                        writer.writerow([
                            summary.period.periodo,
                            summary.employee.codigo_ficha,
                            field_name,
                            int(expected),
                            int(actual),
                            int(difference),
                        ])

                for source_code, field_name in SOURCE_CODE_TO_SUMMARY_FIELD.items():
                    expected = source_code_sums[key].get(source_code, Decimal("0"))
                    actual = getattr(summary, field_name) or Decimal("0")
                    difference = actual - expected
                    if difference:
                        mismatch_count += 1
                        writer.writerow([
                            summary.period.periodo,
                            summary.employee.codigo_ficha,
                            field_name,
                            int(actual),
                            int(expected),
                            int(difference),
                        ])

        self.stdout.write(f"Liquidaciones revisadas: {checked_count}")
        self.stdout.write(f"Diferencias detectadas: {mismatch_count}")
        self.stdout.write(f"Reporte: {output}")
        if mismatch_count and options["fail_on_mismatch"]:
            raise SystemExit(1)
