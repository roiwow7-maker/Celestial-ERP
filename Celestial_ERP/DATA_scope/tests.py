import shutil
import sqlite3
from unittest.mock import patch
from uuid import uuid4

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from Applet.models import AuditLog
from Applet.services import CUSTOM_PERMISSIONS, ROLE_NAMES
from Applet.services import ensure_role_groups
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from DATA_scope.management.commands.backup_sqlite import Command as BackupCommand
from DATA_scope.management.commands.check_sqlite_operational_health import Command as SQLiteHealthCommand
from DATA_scope.management.commands.cleanup_uploads import Command as CleanupUploadsCommand
from DATA_scope.management.commands.validate_backup_restore import Command as ValidateBackupRestoreCommand
from DATA_scope.management.commands.import_payroll_data import (
    TRANSFORMED_REQUIRED_COLUMNS,
    csv_headers,
    validate_columns,
)
from DATA_scope.management.commands.validate_business_rules import SUMMARY_FIELD_TO_CATEGORIES
from DATA_scope.models import Employee, ImportRun, PayrollPeriod
from DATA_scope.quality import validate_transformed_csv, write_quality_report


class PayrollPeriodTests(TestCase):
    def test_period_str_returns_period_code(self):
        period = PayrollPeriod(periodo="202606", year=2026, month=6)
        self.assertEqual(str(period), "202606")


class ImportRunTests(TestCase):
    def test_import_run_defaults_to_started(self):
        run = ImportRun.objects.create(
            transformed_path="../transformed.csv",
            summaries_path="../csv_equivalentes_liquidaciones/Liquidaciones.csv",
        )
        self.assertEqual(run.status, ImportRun.STATUS_STARTED)


class ImportValidationTests(TestCase):
    def setUp(self):
        self.test_dir = settings.BASE_DIR / ".test_artifacts"
        self.test_dir.mkdir(exist_ok=True)

    def tearDown(self):
        for path in self.test_dir.glob("*.csv"):
            path.unlink()

    def test_csv_headers_reads_semicolon_headers(self):
        path = self.test_dir / "sample.csv"
        path.write_text("periodo;codigo;monto\n202606;1;10\n", encoding="utf-8")
        self.assertEqual(csv_headers(path), {"periodo", "codigo", "monto"})

    def test_validate_columns_accepts_required_transformed_columns(self):
        path = self.test_dir / "transformed.csv"
        path.write_text(";".join(sorted(TRANSFORMED_REQUIRED_COLUMNS)) + "\n", encoding="utf-8")
        validate_columns(path, TRANSFORMED_REQUIRED_COLUMNS, "transformed")

    def test_quality_report_detects_invalid_rows_and_duplicates(self):
        path = self.test_dir / "quality.csv"
        path.write_text(
            "periodo;codigo;Rut;nombre;codigo_item;categoria_item;monto\n"
            "202606;1;1-9;Persona;A000;totales;100\n"
            "202606;1;1-9;Persona;A000;totales;100\n"
            "2026;2;2-7;;B000;totales;abc\n",
            encoding="utf-8",
        )
        issues = validate_transformed_csv(path)
        self.assertGreaterEqual(len(issues), 3)
        report_path = self.test_dir / "quality_report.csv"
        write_quality_report(report_path, issues)
        self.assertIn("Movimiento duplicado", report_path.read_text(encoding="utf-8-sig"))


class ManualEmployeeFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        ensure_role_groups()
        User = get_user_model()
        cls.rrhh = User.objects.create_user(username="rrhh", password="test")
        cls.rrhh.groups.add(Group.objects.get(name="RRHH"))
        cls.readonly = User.objects.create_user(username="readonly", password="test")
        cls.readonly.groups.add(Group.objects.get(name="Solo lectura"))

    def test_rrhh_can_create_employee_and_audit_event_is_recorded(self):
        self.client.force_login(self.rrhh)
        response = self.client.post(
            reverse("data_scope:employee_create"),
            {
                "codigo_ficha": "T-001",
                "rut": "11111111-1",
                "nombre": "Trabajador Manual",
                "estado": Employee.STATUS_ACTIVE,
                "division": "RRHH",
                "afp": "",
                "isapre": "",
                "fecha_ingreso": "",
                "fecha_retiro": "",
                "horario_trabajo": "",
                "jornada_vs": "",
                "jornada_contrato": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Employee.objects.filter(codigo_ficha="T-001").exists())
        self.assertTrue(AuditLog.objects.filter(action="employee_created").exists())

    def test_readonly_cannot_create_employee(self):
        self.client.force_login(self.readonly)
        response = self.client.get(reverse("data_scope:employee_create"))
        self.assertEqual(response.status_code, 403)


class BackupCommandTests(TestCase):
    def test_backup_command_is_registered(self):
        self.assertEqual(BackupCommand.help, "Crea un respaldo local de la base SQLite del ERP.")

    def test_backup_command_creates_recoverable_sqlite_copy(self):
        output_dir = settings.BASE_DIR / ".test_artifacts" / f"backup_policy_{uuid4().hex}"
        output_dir.mkdir(parents=True)
        source_path = output_dir / f"source_{uuid4().hex}.sqlite3"
        try:
            with sqlite3.connect(source_path) as connection:
                connection.execute("create table probe (id integer primary key, value text)")
                connection.execute("insert into probe (value) values ('ok')")
            test_databases = {
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": source_path,
                }
            }
            with patch.object(settings, "DATABASES", test_databases):
                call_command("backup_sqlite", output_dir=output_dir)
            backups = list(output_dir.glob("db_*.sqlite3"))
            self.assertEqual(len(backups), 1)
            with sqlite3.connect(backups[0]) as connection:
                result = connection.execute("pragma integrity_check").fetchone()[0]
                value = connection.execute("select value from probe").fetchone()[0]
            self.assertEqual(result, "ok")
            self.assertEqual(value, "ok")
        finally:
            shutil.rmtree(output_dir, ignore_errors=True)

    def test_validate_backup_restore_command_is_registered(self):
        self.assertEqual(
            ValidateBackupRestoreCommand.help,
            "Valida restauracion de un backup SQLite en copia temporal sin tocar la base activa.",
        )

    def test_validate_backup_restore_accepts_valid_sqlite_backup(self):
        output_dir = settings.BASE_DIR / ".test_artifacts" / f"restore_validation_{uuid4().hex}"
        output_dir.mkdir(parents=True)
        backup_path = output_dir / "db_20260714_000000.sqlite3"
        try:
            with sqlite3.connect(backup_path) as connection:
                for table in [
                    "data_employee",
                    "data_payroll_period",
                    "data_payroll_item",
                    "data_payroll_entry",
                    "data_payroll_summary",
                    "Applet_auditlog",
                ]:
                    connection.execute(f'create table "{table}" (id integer primary key)')
            call_command("validate_backup_restore", backup_path=backup_path)
        finally:
            shutil.rmtree(output_dir, ignore_errors=True)


class OperationalCommandTests(TestCase):
    def test_access_roles_are_defined(self):
        self.assertIn("Administrador", ROLE_NAMES)
        self.assertIn("RRHH", ROLE_NAMES)
        self.assertIn("Contabilidad", ROLE_NAMES)
        self.assertIn("Solo lectura", ROLE_NAMES)
        self.assertIn("DATA_scope.upload_payroll_data", CUSTOM_PERMISSIONS["RRHH"])

    def test_business_rule_validation_includes_non_taxable_allowances(self):
        categories = SUMMARY_FIELD_TO_CATEGORIES["total_haberes_no_imponibles"]
        self.assertIn("haberes_exentos_no_imponibles", categories)
        self.assertIn("asignaciones_familiares", categories)

    def test_cleanup_uploads_command_is_registered(self):
        self.assertEqual(
            CleanupUploadsCommand.help,
            "Limpia carpetas antiguas de uploads para reducir exposicion de datos sensibles.",
        )

    def test_sqlite_health_command_is_registered(self):
        self.assertEqual(
            SQLiteHealthCommand.help,
            "Revisa salud operativa de SQLite, backups y volumen base sin requerir PostgreSQL.",
        )
