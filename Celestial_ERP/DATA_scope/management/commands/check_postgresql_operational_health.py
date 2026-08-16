from __future__ import annotations

import shutil
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.utils import timezone

from Applet.services import latest_backup_file


class Command(BaseCommand):
    help = "Monitorea conexion, capacidad, actividad, logs y backup PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument("--fail-on-warning", action="store_true")
        parser.add_argument("--max-backup-age-hours", type=int, default=26)
        parser.add_argument("--min-free-disk-gb", type=float, default=2.0)

    def handle(self, *args, **options):
        if connection.vendor != "postgresql":
            raise CommandError("Este diagnostico requiere PostgreSQL.")
        warnings = []
        with connection.cursor() as cursor:
            cursor.execute("select current_database(), current_user, current_setting('server_version')")
            database, user, version = cursor.fetchone()
            cursor.execute("select pg_database_size(current_database())")
            database_size = cursor.fetchone()[0]
            cursor.execute("select count(*) from pg_stat_activity where datname=current_database()")
            connections = cursor.fetchone()[0]
            cursor.execute(
                "select xact_commit, xact_rollback, deadlocks from pg_stat_database where datname=current_database()"
            )
            commits, rollbacks, deadlocks = cursor.fetchone()

        disk = shutil.disk_usage(settings.PROJECT_ROOT)
        free_gb = disk.free / 1024**3
        if free_gb < options["min_free_disk_gb"]:
            warnings.append(f"Espacio libre bajo: {free_gb:.2f} GB")

        latest = latest_backup_file()
        backup_age = None
        if not latest or latest.get("engine") != "PostgreSQL":
            warnings.append("No existe backup PostgreSQL registrado.")
        else:
            modified = datetime.fromtimestamp(latest["modified_at"], tz=timezone.get_current_timezone())
            backup_age = (timezone.now() - modified).total_seconds() / 3600
            if backup_age > options["max_backup_age_hours"]:
                warnings.append(f"Backup PostgreSQL antiguo: {backup_age:.1f} horas")

        log_path = settings.LOG_DIR / "celestial_erp.log"
        if not log_path.exists():
            warnings.append("Log principal aun no existe.")

        self.stdout.write(f"Base: {database} | Usuario: {user} | PostgreSQL: {version}")
        self.stdout.write(f"Tamano DB: {database_size / 1024**2:.2f} MB | Conexiones: {connections}")
        self.stdout.write(f"Commits: {commits} | Rollbacks: {rollbacks} | Deadlocks: {deadlocks}")
        self.stdout.write(f"Disco libre: {free_gb:.2f} GB")
        self.stdout.write(f"Ultimo backup: {latest['name'] if latest else 'ninguno'}")
        if backup_age is not None:
            self.stdout.write(f"Edad backup: {backup_age:.1f} horas")
        for warning in warnings:
            self.stdout.write(self.style.WARNING("ADVERTENCIA: " + warning))
        if warnings and options["fail_on_warning"]:
            raise CommandError(f"Salud operacional con {len(warnings)} advertencia(s).")
        self.stdout.write(self.style.SUCCESS("Diagnostico PostgreSQL completado."))
