from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from Applet.services import latest_backup_file


REQUIRED_TABLES = [
    "data_employee",
    "data_payroll_period",
    "data_payroll_item",
    "data_payroll_entry",
    "data_payroll_summary",
    "Applet_auditlog",
]


class Command(BaseCommand):
    help = "Valida restauracion de un backup SQLite en copia temporal sin tocar la base activa."

    def add_arguments(self, parser):
        parser.add_argument(
            "--backup-path",
            type=Path,
            default=None,
            help="Ruta del backup SQLite a validar. Si se omite, usa el ultimo backup operativo.",
        )
        parser.add_argument(
            "--keep-restored-copy",
            action="store_true",
            help="Conserva la copia restaurada en .test_artifacts para inspeccion manual.",
        )

    def handle(self, *args, **options):
        database = settings.DATABASES["default"]
        if database["ENGINE"] != "django.db.backends.sqlite3":
            raise CommandError("Este comando solo valida backups SQLite.")

        backup_path = options["backup_path"] or self.latest_backup_path()
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise CommandError(f"No existe el backup a validar: {backup_path}")
        if backup_path.stat().st_size <= 0:
            raise CommandError(f"El backup esta vacio: {backup_path}")

        if options["keep_restored_copy"]:
            restore_dir = settings.BASE_DIR / ".test_artifacts" / "restore_validation"
            restore_dir.mkdir(parents=True, exist_ok=True)
            restored_path = restore_dir / f"restored_{backup_path.name}"
            self.validate_restored_copy(backup_path, restored_path)
            self.stdout.write(self.style.SUCCESS(f"Copia restaurada conservada: {restored_path}"))
            return

        restored_path = backup_path.with_name(f"restore_probe_{backup_path.name}")
        try:
            self.validate_restored_copy(backup_path, restored_path)
        finally:
            self.safe_unlink(restored_path)

    def latest_backup_path(self) -> Path:
        latest_backup = latest_backup_file()
        if not latest_backup:
            raise CommandError("No hay backups registrados en la carpeta operativa.")
        return Path(latest_backup["path"])

    def validate_restored_copy(self, backup_path: Path, restored_path: Path) -> None:
        self.safe_unlink(restored_path)
        shutil.copy2(backup_path, restored_path)
        connection = sqlite3.connect(restored_path)
        try:
            integrity = connection.execute("pragma integrity_check").fetchone()[0]
            if integrity != "ok":
                raise CommandError(f"Restauracion invalida segun integrity_check: {integrity}")

            existing_tables = {
                row[0]
                for row in connection.execute(
                    "select name from sqlite_master where type = 'table'"
                ).fetchall()
            }
            missing_tables = [table for table in REQUIRED_TABLES if table not in existing_tables]
            if missing_tables:
                raise CommandError(
                    "Restauracion incompleta. Faltan tablas: " + ", ".join(missing_tables)
                )

            counts = {
                table: connection.execute(f'select count(*) from "{table}"').fetchone()[0]
                for table in REQUIRED_TABLES
            }
        finally:
            connection.close()

        self.stdout.write(self.style.SUCCESS(f"Restauracion validada desde backup: {backup_path}"))
        self.stdout.write("Conteos verificados: " + ", ".join(f"{table}={count}" for table, count in counts.items()))

    def safe_unlink(self, path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except PermissionError:
            self.stdout.write(self.style.WARNING(f"No se pudo borrar copia temporal bloqueada por Windows: {path}"))
