from __future__ import annotations

import shutil
import socket
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from Applet.services import latest_backup_file


REQUIRED_TABLES = {
    "data_employee",
    "data_payroll_period",
    "data_payroll_item",
    "data_payroll_entry",
    "data_payroll_summary",
    "Applet_auditlog",
    "auth_user",
}


def postgres_tool(name: str) -> str:
    direct = shutil.which(name)
    if direct:
        return direct
    candidates = sorted(Path("/usr/lib/postgresql").glob(f"*/bin/{name}"), reverse=True)
    if candidates:
        return str(candidates[0])
    raise CommandError(f"No se encontro la herramienta PostgreSQL: {name}")


class Command(BaseCommand):
    help = "Restaura y valida un dump PostgreSQL en un cluster temporal completamente aislado."

    def add_arguments(self, parser):
        parser.add_argument("--backup-path", type=Path, default=None)
        parser.add_argument("--keep-cluster", action="store_true")

    def handle(self, *args, **options):
        backup = options["backup_path"] or self.latest_postgresql_backup()
        backup = Path(backup).resolve()
        if not backup.exists() or backup.stat().st_size == 0:
            raise CommandError(f"Backup PostgreSQL inexistente o vacio: {backup}")

        tools = {name: postgres_tool(name) for name in ("initdb", "pg_ctl", "createdb", "pg_restore", "psql")}
        root = Path(tempfile.mkdtemp(prefix="celestial_pg_restore_"))
        data_dir = root / "data"
        socket_dir = root / "socket"
        socket_dir.mkdir()
        port = self.available_port()
        started = False

        try:
            self.run([tools["initdb"], "-D", str(data_dir), "-A", "trust", "-U", "postgres", "--no-locale"])
            self.run([
                tools["pg_ctl"], "-D", str(data_dir), "-l", str(root / "postgres.log"), "-o",
                f"-F -p {port} -k {socket_dir}", "-w", "start",
            ])
            started = True
            common = ["-h", str(socket_dir), "-p", str(port), "-U", "postgres"]
            self.run([tools["createdb"], *common, "celestial_restore_probe"])
            self.run([
                tools["pg_restore"], *common, "-d", "celestial_restore_probe",
                "--no-owner", "--no-privileges", "--exit-on-error", str(backup),
            ])

            tables_output = self.run([
                tools["psql"], *common, "-d", "celestial_restore_probe", "-At", "-c",
                "select tablename from pg_tables where schemaname='public' order by tablename;",
            ]).stdout
            tables = set(tables_output.splitlines())
            missing = sorted(REQUIRED_TABLES - tables)
            if missing:
                raise CommandError("Restauracion incompleta; faltan tablas: " + ", ".join(missing))

            count_sql = (
                'select (select count(*) from "data_employee"), '
                '(select count(*) from "data_payroll_entry"), '
                '(select count(*) from "data_payroll_summary"), '
                '(select count(*) from "Applet_auditlog"), '
                '(select count(*) from "auth_user");'
            )
            counts = self.run([
                tools["psql"], *common, "-d", "celestial_restore_probe", "-At", "-F", ";", "-c", count_sql,
            ]).stdout.strip()
            self.stdout.write(self.style.SUCCESS(f"Restauracion PostgreSQL validada: {backup}"))
            self.stdout.write("Conteos employee;entry;summary;audit;users: " + counts)
        finally:
            if started:
                subprocess.run([tools["pg_ctl"], "-D", str(data_dir), "-m", "fast", "-w", "stop"], capture_output=True)
            if options["keep_cluster"]:
                self.stdout.write(self.style.WARNING(f"Cluster temporal conservado: {root}"))
            else:
                shutil.rmtree(root, ignore_errors=True)

    def latest_postgresql_backup(self) -> Path:
        latest = latest_backup_file()
        if not latest or latest.get("engine") != "PostgreSQL":
            raise CommandError("No existe un backup PostgreSQL operativo para validar.")
        return Path(latest["path"])

    def available_port(self) -> int:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            return probe.getsockname()[1]

    def run(self, command: list[str]) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or exc.stdout or str(exc)).strip()
            raise CommandError(detail) from exc
