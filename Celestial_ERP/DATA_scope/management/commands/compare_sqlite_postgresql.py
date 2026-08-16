from __future__ import annotations

import sqlite3
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


CHECKS = {
    "employees": ('data_employee', None, "exact"),
    "periods": ('data_payroll_period', None, "exact"),
    "items": ('data_payroll_item', None, "exact"),
    "entries": ('data_payroll_entry', 'monto', "exact"),
    "summaries": ('data_payroll_summary', 'sueldo_liquido', "exact"),
    # PostgreSQL sigue recibiendo auditorias y usuarios despues del corte.
    "audit_logs": ('Applet_auditlog', None, "not_less"),
    "users": ('auth_user', None, "not_less"),
}


class Command(BaseCommand):
    help = "Compara conteos y sumas de control entre SQLite historico y PostgreSQL activo."

    def add_arguments(self, parser):
        parser.add_argument("--sqlite-path", type=Path, default=settings.BASE_DIR / "db.sqlite3")

    def handle(self, *args, **options):
        sqlite_path = options["sqlite_path"].resolve()
        if not sqlite_path.exists():
            raise CommandError(f"No existe SQLite historico: {sqlite_path}")
        mismatches = []
        uri = f"file:{sqlite_path}?mode=ro"
        with sqlite3.connect(uri, uri=True) as sqlite_db, connection.cursor() as postgres:
            for label, (table, sum_field, comparison) in CHECKS.items():
                sqlite_value = self.metric(sqlite_db, table, sum_field)
                postgres.execute(self.metric_sql(table, sum_field))
                postgres_value = postgres.fetchone()[0] or 0
                if sum_field:
                    sqlite_value = Decimal(str(sqlite_value))
                    postgres_value = Decimal(str(postgres_value))
                matches = sqlite_value == postgres_value if comparison == "exact" else postgres_value >= sqlite_value
                status = "OK" if matches else "DIFERENCIA"
                self.stdout.write(f"{label}: SQLite={sqlite_value} PostgreSQL={postgres_value} [{status}]")
                if status != "OK":
                    mismatches.append(label)
        if mismatches:
            raise CommandError("Comparacion con diferencias: " + ", ".join(mismatches))
        self.stdout.write(self.style.SUCCESS("SQLite y PostgreSQL coinciden en todos los controles."))

    def metric(self, database, table: str, sum_field: str | None):
        return database.execute(self.metric_sql(table, sum_field)).fetchone()[0] or 0

    def metric_sql(self, table: str, sum_field: str | None) -> str:
        if sum_field:
            return f'SELECT COALESCE(SUM("{sum_field}"), 0) FROM "{table}"'
        return f'SELECT COUNT(*) FROM "{table}"'
