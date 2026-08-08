from __future__ import annotations

import csv
import hashlib
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from DATA_scope.models import Employee, ImportRun, PayrollEntry, PayrollItem, PayrollPeriod, PayrollSummary


CSV_SEPARATOR = ";"
DEFAULT_TRANSFORMED = Path("../transformed.csv")
DEFAULT_SUMMARIES = Path("../csv_equivalentes_liquidaciones/Liquidaciones.csv")
DEFAULT_DESCRIPTIONS_DIR = Path("../descripciones_codigo_item")
BULK_SIZE = 5000

TRANSFORMED_REQUIRED_COLUMNS = {
    "periodo",
    "codigo",
    "Rut",
    "nombre",
    "Division",
    "Codigo A.F.P.",
    "Isapre",
    "diastr",
    "codigo_item",
    "categoria_item",
    "requiere_confirmacion",
    "monto",
}

DESCRIPTION_ALIASES = {
    "DIASTR1": "DIASTR",
    "ISAPRE1": "ISAPRE",
}

SUMMARY_FIELD_MAP = {
    "Sueldo Base*": "sueldo_base",
    "Días Laborales*": "dias_laborales",
    "Días Trabajados*": "dias_trabajados",
    "Días Licencias*": "dias_licencias",
    "Días Permisos*": "dias_permisos",
    "Días Ausencias*": "dias_ausencias",
    "Días Suspendidos*": "dias_suspendidos",
    "Número Horas No Trabajadas*": "horas_no_trabajadas",
    "Sobretiempo horas extras*": "horas_extras",
    "Costo Empresa*": "costo_empresa",
    "Total Haberes Imponibles*": "total_haberes_imponibles",
    "Total Haberes No Imponibles No Tributables*": "total_haberes_no_imponibles",
    "Total Haberes No Imponibles Tributables*": "total_haberes_no_imponibles_tributables",
    "Total Descuentos Legales*": "total_descuentos_legales",
    "Total Otros Descuentos*": "total_otros_descuentos",
    "Sueldo Líquido*": "sueldo_liquido",
    "Base Tributable*": "base_tributable",
    "Impuesto*": "impuesto",
    "Pago Previsión*": "pago_prevision",
    "Pago Salud Obligatoria*": "pago_salud_obligatoria",
    "Pago Salud Voluntaria*": "pago_salud_voluntaria",
    "Pago Previsión Voluntaria*": "pago_prevision_voluntaria",
    "Seguro Cesantía (Trabajador)*": "seguro_cesantia_trabajador",
    "Seguro Cesantia (Empleador)": "seguro_cesantia_empleador",
    "Mutual Empleador": "mutual_empleador",
    "Pago SIS (Empleador)": "pago_sis_empleador",
    "AFP prevision empleador": "afp_prevision_empleador",
    "Ley Sanna (Ley protección empleo)": "ley_sanna",
    "Otros Aportes Patronales": "otros_aportes_patronales",
    "Saldo Sobregiro*": "saldo_sobregiro",
}

INTEGER_SUMMARY_FIELDS = {
    "dias_laborales",
    "dias_trabajados",
    "dias_licencias",
    "dias_permisos",
    "dias_ausencias",
    "dias_suspendidos",
}

SUMMARY_REQUIRED_COLUMNS = set(SUMMARY_FIELD_MAP.keys()) | {
    "Número de Documento*",
    "Código de Ficha",
    "RUT Empresa*",
}


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_headers(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=CSV_SEPARATOR)
        try:
            return {clean(value) for value in next(reader)}
        except StopIteration:
            return set()


def validate_columns(path: Path, required: set[str], label: str) -> None:
    headers = csv_headers(path)
    missing = sorted(required - headers)
    if missing:
        raise CommandError(f"Faltan columnas en {label}: {', '.join(missing)}")


def as_decimal(value: object) -> Decimal:
    text = clean(value)
    if not text:
        return Decimal("0")
    try:
        return Decimal(text.replace(",", "."))
    except InvalidOperation:
        return Decimal("0")


def as_int(value: object) -> int:
    return int(as_decimal(value))


def parse_datetime(value: object):
    text = clean(value)
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def period_parts(periodo: str) -> tuple[int, int]:
    text = clean(periodo)
    if len(text) != 6 or not text.isdigit():
        return 0, 0
    return int(text[:4]), int(text[4:])


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle, delimiter=CSV_SEPARATOR)


def read_descriptions(descriptions_dir: Path) -> dict[str, str]:
    descriptions = {}
    if not descriptions_dir.exists():
        return descriptions

    for path in sorted(descriptions_dir.glob("*_descripciones.csv")):
        if path.name == "todos_los_codigo_item_descripciones.csv":
            continue
        for row in read_csv(path):
            code = clean(row.get("codigo_item"))
            description = clean(row.get("descripcion"))
            if code and description:
                descriptions[code] = description

    for source_code, description_code in DESCRIPTION_ALIASES.items():
        if source_code not in descriptions and description_code in descriptions:
            descriptions[source_code] = descriptions[description_code]
    return descriptions


class Command(BaseCommand):
    help = "Importa los datos ETL de liquidaciones a los modelos de DATA_scope."

    def add_arguments(self, parser):
        parser.add_argument("--transformed", type=Path, default=DEFAULT_TRANSFORMED)
        parser.add_argument("--summaries", type=Path, default=DEFAULT_SUMMARIES)
        parser.add_argument("--descriptions-dir", type=Path, default=DEFAULT_DESCRIPTIONS_DIR)
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Borra datos previos de DATA_scope antes de importar.",
        )

    def handle(self, *args, **options):
        transformed_path: Path = options["transformed"]
        summaries_path: Path = options["summaries"]
        descriptions_dir: Path = options["descriptions_dir"]

        if not transformed_path.exists():
            raise CommandError(f"No existe transformed.csv: {transformed_path}")
        if not summaries_path.exists():
            raise CommandError(f"No existe Liquidaciones.csv: {summaries_path}")

        validate_columns(transformed_path, TRANSFORMED_REQUIRED_COLUMNS, "transformed")
        validate_columns(summaries_path, SUMMARY_REQUIRED_COLUMNS, "summaries")

        import_run = ImportRun.objects.create(
            transformed_path=str(transformed_path),
            summaries_path=str(summaries_path),
            descriptions_dir=str(descriptions_dir),
            transformed_sha256=sha256_file(transformed_path),
            summaries_sha256=sha256_file(summaries_path),
            clear_requested=options["clear"],
        )

        try:
            descriptions = read_descriptions(descriptions_dir)
            transformed_rows = list(read_csv(transformed_path))

            with transaction.atomic():
                if options["clear"]:
                    self.clear_data()

                employees = self.import_employees(transformed_rows)
                periods = self.import_periods(transformed_rows)
                items = self.import_items(transformed_rows, descriptions)
                entries_count = self.import_entries(transformed_rows, employees, periods, items)
                summaries_count = self.import_summaries(summaries_path, employees, periods)
        except Exception as exc:
            import_run.status = ImportRun.STATUS_FAILED
            import_run.error_message = str(exc)
            import_run.save(update_fields=["status", "error_message", "updated_at"])
            raise

        import_run.status = ImportRun.STATUS_SUCCESS
        import_run.employee_count = len(employees)
        import_run.period_count = len(periods)
        import_run.item_count = len(items)
        import_run.entry_count = entries_count
        import_run.summary_count = summaries_count
        import_run.save()

        self.stdout.write(self.style.SUCCESS("Importacion completada"))
        self.stdout.write(f"ImportRun: {import_run.id}")
        self.stdout.write(f"Employees: {len(employees)}")
        self.stdout.write(f"PayrollPeriod: {len(periods)}")
        self.stdout.write(f"PayrollItem: {len(items)}")
        self.stdout.write(f"PayrollEntry: {entries_count}")
        self.stdout.write(f"PayrollSummary: {summaries_count}")

    def clear_data(self) -> None:
        PayrollSummary.objects.all().delete()
        PayrollEntry.objects.all().delete()
        PayrollItem.objects.all().delete()
        PayrollPeriod.objects.all().delete()
        Employee.objects.all().delete()

    def import_employees(self, rows: list[dict[str, str]]) -> dict[str, Employee]:
        by_code = {}
        for row in rows:
            code = clean(row.get("codigo"))
            if not code or code in by_code:
                continue
            by_code[code] = Employee(
                codigo_ficha=code,
                rut=clean(row.get("Rut")),
                nombre=clean(row.get("nombre")),
                division=clean(row.get("Division")),
                afp=clean(row.get("Codigo A.F.P.")),
                isapre=clean(row.get("Isapre")),
                fecha_ingreso=parse_datetime(row.get("Fecha de Ingreso")),
                fecha_retiro=parse_datetime(row.get("Fecha de Retiro")),
                horario_trabajo=clean(row.get("Horario de trabajo")),
                jornada_vs=clean(row.get("Jornada: V / S")),
                jornada_contrato=clean(row.get("Jornada de contrato")),
            )

        Employee.objects.bulk_create(by_code.values(), batch_size=BULK_SIZE, ignore_conflicts=True)
        return {employee.codigo_ficha: employee for employee in Employee.objects.all()}

    def import_periods(self, rows: list[dict[str, str]]) -> dict[str, PayrollPeriod]:
        periods = {}
        for row in rows:
            periodo = clean(row.get("periodo"))
            if not periodo or periodo in periods:
                continue
            year, month = period_parts(periodo)
            periods[periodo] = PayrollPeriod(periodo=periodo, year=year, month=month)

        PayrollPeriod.objects.bulk_create(periods.values(), batch_size=BULK_SIZE, ignore_conflicts=True)
        return {period.periodo: period for period in PayrollPeriod.objects.all()}

    def import_items(
        self,
        rows: list[dict[str, str]],
        descriptions: dict[str, str],
    ) -> dict[str, PayrollItem]:
        items = {}
        for row in rows:
            code = clean(row.get("codigo_item"))
            if not code or code in items:
                continue
            items[code] = PayrollItem(
                codigo=code,
                categoria=clean(row.get("categoria_item")),
                descripcion=descriptions.get(code, ""),
                requiere_confirmacion=clean(row.get("requiere_confirmacion")).lower() == "true",
            )

        PayrollItem.objects.bulk_create(items.values(), batch_size=BULK_SIZE, ignore_conflicts=True)
        return {item.codigo: item for item in PayrollItem.objects.all()}

    def import_entries(
        self,
        rows: list[dict[str, str]],
        employees: dict[str, Employee],
        periods: dict[str, PayrollPeriod],
        items: dict[str, PayrollItem],
    ) -> int:
        entries = []
        count = 0
        for row in rows:
            employee = employees[clean(row.get("codigo"))]
            period = periods[clean(row.get("periodo"))]
            item = items[clean(row.get("codigo_item"))]
            entries.append(
                PayrollEntry(
                    employee=employee,
                    period=period,
                    item=item,
                    monto=as_decimal(row.get("monto")),
                )
            )
            if len(entries) >= BULK_SIZE:
                PayrollEntry.objects.bulk_create(entries, batch_size=BULK_SIZE, ignore_conflicts=True)
                count += len(entries)
                entries.clear()

        if entries:
            PayrollEntry.objects.bulk_create(entries, batch_size=BULK_SIZE, ignore_conflicts=True)
            count += len(entries)
        return count

    def import_summaries(
        self,
        summaries_path: Path,
        employees: dict[str, Employee],
        periods: dict[str, PayrollPeriod],
    ) -> int:
        summaries = []
        for row in read_csv(summaries_path):
            document_number = clean(row.get("Número de Documento*"))
            code = clean(row.get("Código de Ficha"))
            period_code = document_number.split("-", 1)[0]
            summary = PayrollSummary(
                document_number=document_number,
                employee=employees[code],
                period=periods[period_code],
                rut_empresa=clean(row.get("RUT Empresa*")),
            )

            for csv_field, model_field in SUMMARY_FIELD_MAP.items():
                if model_field in INTEGER_SUMMARY_FIELDS:
                    setattr(summary, model_field, as_int(row.get(csv_field)))
                else:
                    setattr(summary, model_field, as_decimal(row.get(csv_field)))
            summaries.append(summary)

        PayrollSummary.objects.bulk_create(summaries, batch_size=BULK_SIZE, ignore_conflicts=True)
        return len(summaries)
