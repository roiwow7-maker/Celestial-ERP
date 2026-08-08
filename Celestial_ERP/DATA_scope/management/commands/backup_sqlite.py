from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crea un respaldo local de la base SQLite del ERP."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=Path,
            default=settings.PROJECT_ROOT / "backups",
            help="Carpeta donde se guardara el respaldo.",
        )
        parser.add_argument("--retention-days", type=int, default=0, help="Borra backups mas antiguos que N dias.")
        parser.add_argument("--keep-last", type=int, default=0, help="Conserva al menos los ultimos N backups.")
        parser.add_argument("--no-verify", action="store_true", help="No ejecuta pragma integrity_check sobre el backup.")

    def handle(self, *args, **options):
        database = settings.DATABASES["default"]
        if database["ENGINE"] != "django.db.backends.sqlite3":
            raise CommandError("Este comando solo aplica a SQLite.")

        source = Path(database["NAME"])
        if not source.exists():
            raise CommandError(f"No existe la base SQLite: {source}")

        output_dir: Path = options["output_dir"]
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = output_dir / f"db_{timestamp}.sqlite3"
        self.create_sqlite_backup(source, target)
        if not options["no_verify"]:
            self.verify_backup(target)
        self.apply_retention(output_dir, options["retention_days"], options["keep_last"])
        self.stdout.write(self.style.SUCCESS(f"Backup creado: {target}"))

    def create_sqlite_backup(self, source: Path, target: Path) -> None:
        with sqlite3.connect(source) as source_connection:
            with sqlite3.connect(target) as target_connection:
                source_connection.backup(target_connection)
        shutil.copystat(source, target)

    def verify_backup(self, target: Path) -> None:
        with sqlite3.connect(target) as connection:
            result = connection.execute("pragma integrity_check").fetchone()[0]
        if result != "ok":
            target.unlink(missing_ok=True)
            raise CommandError(f"Backup corrupto segun integrity_check: {result}")

    def apply_retention(self, output_dir: Path, retention_days: int, keep_last: int) -> None:
        if retention_days <= 0:
            return
        backups = sorted(output_dir.glob("db_*.sqlite3"), key=lambda path: path.stat().st_mtime, reverse=True)
        protected = set(backups[: max(keep_last, 0)])
        cutoff = datetime.now().timestamp() - (retention_days * 24 * 60 * 60)
        for path in backups:
            if path in protected:
                continue
            if path.stat().st_mtime < cutoff:
                path.unlink()
                self.stdout.write(f"Backup antiguo eliminado: {path}")
