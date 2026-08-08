from __future__ import annotations

import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from Applet.services import latest_backup_file
from Attendance.models import AttendanceRecord
from DATA_scope.models import Employee, ImportRun, PayrollEntry, PayrollItem, PayrollPeriod, PayrollSummary


class Command(BaseCommand):
    help = "Revisa salud operativa de SQLite, backups y volumen base sin requerir PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fail-on-warning",
            action="store_true",
            help="Retorna error si existen advertencias operativas.",
        )

    def handle(self, *args, **options):
        ok: list[str] = []
        warnings: list[str] = []

        database = settings.DATABASES["default"]
        if database["ENGINE"] != "django.db.backends.sqlite3":
            raise CommandError("Este diagnostico solo aplica cuando la base activa es SQLite.")

        db_path = Path(database["NAME"])
        if not db_path.exists():
            raise CommandError(f"No existe la base SQLite configurada: {db_path}")

        size_mb = db_path.stat().st_size / (1024 * 1024)
        ok.append(f"Base SQLite detectada: {db_path}")
        ok.append(f"Tamano actual: {size_mb:.2f} MB")

        with sqlite3.connect(db_path) as connection:
            integrity = connection.execute("pragma integrity_check").fetchone()[0]
            journal_mode = connection.execute("pragma journal_mode").fetchone()[0]
            connection.execute("pragma foreign_keys = on")
            foreign_keys = connection.execute("pragma foreign_keys").fetchone()[0]

        if integrity == "ok":
            ok.append("integrity_check: ok")
        else:
            warnings.append(f"integrity_check reporta: {integrity}")

        if journal_mode.lower() == "wal":
            ok.append("journal_mode: WAL")
        else:
            warnings.append(f"journal_mode no esta en WAL: {journal_mode}")

        if foreign_keys:
            ok.append("foreign_keys: ON")
        else:
            warnings.append("foreign_keys aparece desactivado para una conexion nueva.")

        latest_backup = latest_backup_file()
        if latest_backup:
            ok.append(f"Ultimo backup registrado: {latest_backup['name']} ({latest_backup['size_mb']} MB)")
        else:
            warnings.append("No hay backup SQLite registrado en la carpeta operativa.")

        uploads_dir = settings.PROJECT_ROOT / "uploads"
        if uploads_dir.exists():
            upload_runs = len([path for path in uploads_dir.iterdir() if path.is_dir()])
            if upload_runs > 30:
                warnings.append(f"uploads contiene {upload_runs} carpetas. Evaluar cleanup_uploads.")
            else:
                ok.append(f"uploads controlado: {upload_runs} carpetas.")
        else:
            ok.append("uploads aun no existe o no tiene corridas guardadas.")

        counts = {
            "trabajadores": Employee.objects.count(),
            "periodos": PayrollPeriod.objects.count(),
            "items": PayrollItem.objects.count(),
            "movimientos": PayrollEntry.objects.count(),
            "liquidaciones": PayrollSummary.objects.count(),
            "cargas": ImportRun.objects.count(),
            "asistencia": AttendanceRecord.objects.count(),
        }
        ok.append(
            "Conteos base: "
            + ", ".join(f"{name}={value}" for name, value in counts.items())
        )

        if counts["movimientos"] > 500000:
            warnings.append("El volumen de movimientos supera 500000; evitar escrituras concurrentes en SQLite.")

        self.stdout.write(self.style.SUCCESS("Salud operativa SQLite:"))
        for message in ok:
            self.stdout.write(f"- {message}")

        if warnings:
            self.stdout.write(self.style.WARNING("\nAdvertencias:"))
            for message in warnings:
                self.stdout.write(f"- {message}")
            if options["fail_on_warning"]:
                raise SystemExit(1)
            return

        self.stdout.write(self.style.SUCCESS("\nSin advertencias operativas SQLite."))
