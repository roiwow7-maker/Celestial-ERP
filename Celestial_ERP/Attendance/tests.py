from __future__ import annotations

from datetime import date, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from DATA_scope.models import Employee, PayrollPeriod, PayrollSummary

from .models import AttendanceRecord
from .payroll_sync import sync_attendance_to_payroll
from .services import attendance_summary, monthly_employee_rows


class AttendanceRecordTests(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(codigo_ficha="1001", rut="11.111.111-1", nombre="Trabajadora Uno")

    def test_worked_hours_discount_break(self):
        record = AttendanceRecord.objects.create(
            employee=self.employee,
            date=date(2026, 7, 13),
            check_in=time(8, 30),
            check_out=time(17, 30),
            break_minutes=60,
            status=AttendanceRecord.STATUS_PRESENT,
        )

        self.assertEqual(record.worked_minutes, 480)
        self.assertEqual(record.worked_hours, Decimal("8.00"))

    def test_worked_hours_supports_overnight_shift(self):
        record = AttendanceRecord.objects.create(
            employee=self.employee,
            date=date(2026, 7, 13),
            check_in=time(22, 0),
            check_out=time(6, 0),
            status=AttendanceRecord.STATUS_PRESENT,
        )

        self.assertEqual(record.worked_hours, Decimal("8.00"))

    def test_worked_status_requires_check_times(self):
        record = AttendanceRecord(employee=self.employee, date=date(2026, 7, 13), status=AttendanceRecord.STATUS_PRESENT)

        with self.assertRaises(ValidationError):
            record.clean()

    def test_monthly_summary_groups_by_employee(self):
        AttendanceRecord.objects.create(
            employee=self.employee,
            date=date(2026, 7, 13),
            check_in=time(9, 0),
            check_out=time(18, 0),
            break_minutes=60,
            status=AttendanceRecord.STATUS_LATE,
        )

        summary = attendance_summary(AttendanceRecord.objects.all())
        rows = monthly_employee_rows(2026, 7)

        self.assertEqual(summary["records"], 1)
        self.assertEqual(summary["late"], 1)
        self.assertEqual(rows[0]["worked_hours"], Decimal("8.00"))


class AttendanceRouteTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="asistencia", password="test12345")
        for codename in [
            "access_attendance_module",
            "manage_attendance_records",
            "view_attendance_reports",
            "export_attendance_reports",
        ]:
            permission = Permission.objects.get(codename=codename, content_type__app_label="Attendance")
            self.user.user_permissions.add(permission)
        self.employee = Employee.objects.create(codigo_ficha="1002", rut="22.222.222-2", nombre="Trabajador Dos")
        AttendanceRecord.objects.create(
            employee=self.employee,
            date=date(2026, 7, 13),
            check_in=time(8, 0),
            check_out=time(17, 0),
            break_minutes=60,
            status=AttendanceRecord.STATUS_PRESENT,
        )

    def test_dashboard_loads_with_permission(self):
        self.client.login(username="asistencia", password="test12345")
        response = self.client.get(reverse("attendance:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Asistencia")

    def test_monthly_report_loads_with_permission(self):
        self.client.login(username="asistencia", password="test12345")
        response = self.client.get(reverse("attendance:monthly_report"), {"year": 2026, "month": 7})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reporte mensual")

    def test_csv_export_contains_worker_row(self):
        self.client.login(username="asistencia", password="test12345")
        response = self.client.get(reverse("attendance:export_csv"), {"desde": "2026-07-01", "hasta": "2026-07-31"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertContains(response, "Trabajador Dos")


class AttendancePayrollSyncTests(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(codigo_ficha="2001", rut="33.333.333-3", nombre="Trabajadora Sync")
        self.period = PayrollPeriod.objects.create(periodo="202607", year=2026, month=7)
        self.summary = PayrollSummary.objects.create(document_number="SYNC-202607", employee=self.employee, period=self.period)
        AttendanceRecord.objects.create(
            employee=self.employee,
            date=date(2026, 7, 1),
            check_in=time(8, 0),
            check_out=time(17, 0),
            break_minutes=60,
            status=AttendanceRecord.STATUS_PRESENT,
        )
        AttendanceRecord.objects.create(
            employee=self.employee,
            date=date(2026, 7, 2),
            check_in=time(8, 30),
            check_out=time(17, 0),
            break_minutes=60,
            status=AttendanceRecord.STATUS_LATE,
        )
        AttendanceRecord.objects.create(employee=self.employee, date=date(2026, 7, 3), status=AttendanceRecord.STATUS_ABSENT)
        AttendanceRecord.objects.create(employee=self.employee, date=date(2026, 7, 4), status=AttendanceRecord.STATUS_LEAVE)

    def test_sync_updates_payroll_summary_days_and_hours(self):
        rows = sync_attendance_to_payroll("202607")
        self.summary.refresh_from_db()

        self.assertEqual(len(rows), 1)
        self.assertEqual(self.summary.dias_trabajados, 2)
        self.assertEqual(self.summary.dias_ausencias, 1)
        self.assertEqual(self.summary.dias_permisos, 1)
        self.assertEqual(self.summary.horas_no_trabajadas, Decimal("8.00"))

    def test_sync_command_dry_run_does_not_save(self):
        call_command("sync_attendance_payroll", "202607", dry_run=True)
        self.summary.refresh_from_db()

        self.assertEqual(self.summary.dias_trabajados, 0)
