from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crea y verifica un respaldo PostgreSQL en formato custom de pg_dump."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=Path,
            default=settings.PROJECT_ROOT / "backups",
            help="Carpeta donde se guardara el respaldo.",
        )
        parser.add_argument("--retention-days", type=int, default=30)
        parser.add_argument("--keep-last", type=int, default=7)
        parser.add_argument("--no-verify", action="store_true")

    def handle(self, *args, **options):
        database = settings.DATABASES["default"]
        if database["ENGINE"] != "django.db.backends.postgresql":
            raise CommandError("Este comando solo aplica a PostgreSQL.")

        pg_dump = shutil.which("pg_dump")
        pg_restore = shutil.which("pg_restore")
        if not pg_dump:
            raise CommandError("No se encontro pg_dump en PATH.")
        if not options["no_verify"] and not pg_restore:
            raise CommandError("No se encontro pg_restore en PATH.")

        output_dir: Path = options["output_dir"]
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = output_dir / f"postgres_{database['NAME']}_{timestamp}.dump"

        env = os.environ.copy()
        if database.get("PASSWORD"):
            env["PGPASSWORD"] = str(database["PASSWORD"])

        command = [
            pg_dump,
            "--format=custom",
            "--no-owner",
            "--no-privileges",
            "--file",
            str(target),
            "--dbname",
            str(database["NAME"]),
            "--username",
            str(database["USER"]),
            "--host",
            str(database.get("HOST") or "127.0.0.1"),
            "--port",
            str(database.get("PORT") or "5432"),
        ]

        try:
            subprocess.run(command, env=env, check=True, capture_output=True, text=True)
            if not target.exists() or target.stat().st_size == 0:
                raise CommandError("pg_dump termino sin crear un respaldo valido.")
            if not options["no_verify"]:
                subprocess.run(
                    [pg_restore, "--list", str(target)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
        except subprocess.CalledProcessError as exc:
            target.unlink(missing_ok=True)
            detail = (exc.stderr or exc.stdout or str(exc)).strip()
            raise CommandError(f"Fallo el respaldo PostgreSQL: {detail}") from exc

        self.apply_retention(output_dir, options["retention_days"], options["keep_last"])
        size_mb = target.stat().st_size / (1024 * 1024)
        self.stdout.write(self.style.SUCCESS(f"Backup PostgreSQL creado y verificado: {target} ({size_mb:.2f} MB)"))

    def apply_retention(self, output_dir: Path, retention_days: int, keep_last: int) -> None:
        if retention_days <= 0:
            return
        backups = sorted(
            output_dir.glob("postgres_*.dump"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        protected = set(backups[: max(keep_last, 0)])
        cutoff = datetime.now().timestamp() - retention_days * 24 * 60 * 60
        for path in backups:
            if path not in protected and path.stat().st_mtime < cutoff:
                path.unlink()
                self.stdout.write(f"Backup antiguo eliminado: {path}")

