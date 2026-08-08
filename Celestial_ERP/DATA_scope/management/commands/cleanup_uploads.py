from __future__ import annotations

import shutil
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Limpia carpetas antiguas de uploads para reducir exposicion de datos sensibles."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=30, help="Antiguedad minima para borrar carpetas.")
        parser.add_argument("--dry-run", action="store_true", help="Solo lista carpetas que serian eliminadas.")

    def handle(self, *args, **options):
        uploads_dir = settings.PROJECT_ROOT / "uploads"
        if not uploads_dir.exists():
            self.stdout.write("No existe carpeta uploads.")
            return

        cutoff = timezone.now() - timedelta(days=options["days"])
        candidates: list[Path] = []
        for path in uploads_dir.iterdir():
            if not path.is_dir():
                continue
            modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.get_current_timezone())
            if modified < cutoff:
                candidates.append(path)

        for path in candidates:
            if options["dry_run"]:
                self.stdout.write(f"Se eliminaria: {path}")
            else:
                shutil.rmtree(path)
                self.stdout.write(f"Eliminado: {path}")

        self.stdout.write(f"Carpetas evaluadas para limpieza: {len(candidates)}")
