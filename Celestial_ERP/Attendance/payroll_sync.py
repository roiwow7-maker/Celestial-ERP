from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from DATA_scope.models import PayrollPeriod, PayrollSummary

from .models import AttendanceRecord
from .services import period_bounds


@dataclass
class AttendancePayrollSyncRow:
    summary: PayrollSummary
    worked_days: int
    absence_days: int
    leave_days: int
    not_worked_hours: Decimal
    changed: bool


def sync_attendance_to_payroll(period_code: str, *, dry_run: bool = False, hours_per_absence: Decimal = Decimal("8.00")):
    period = PayrollPeriod.objects.get(periodo=period_code)
    start, end = period_bounds(period.year, period.month)
    summaries = PayrollSummary.objects.filter(period=period).select_related("employee", "period")
    rows: list[AttendancePayrollSyncRow] = []

    with transaction.atomic():
        for summary in summaries:
            records = list(AttendanceRecord.objects.filter(employee=summary.employee, date__range=(start, end)))
            worked_days = sum(
                1
                for record in records
                if record.status
                in {
                    AttendanceRecord.STATUS_PRESENT,
                    AttendanceRecord.STATUS_LATE,
                    AttendanceRecord.STATUS_REMOTE,
                }
            )
            absence_days = sum(1 for record in records if record.status == AttendanceRecord.STATUS_ABSENT)
            leave_days = sum(1 for record in records if record.status == AttendanceRecord.STATUS_LEAVE)
            not_worked_hours = (Decimal(absence_days) * hours_per_absence).quantize(Decimal("0.01"))
            changed = (
                summary.dias_trabajados != worked_days
                or summary.dias_ausencias != absence_days
                or summary.dias_permisos != leave_days
                or summary.horas_no_trabajadas != not_worked_hours
            )
            rows.append(
                AttendancePayrollSyncRow(
                    summary=summary,
                    worked_days=worked_days,
                    absence_days=absence_days,
                    leave_days=leave_days,
                    not_worked_hours=not_worked_hours,
                    changed=changed,
                )
            )
            if changed and not dry_run:
                summary.dias_trabajados = worked_days
                summary.dias_ausencias = absence_days
                summary.dias_permisos = leave_days
                summary.horas_no_trabajadas = not_worked_hours
                summary.save(update_fields=["dias_trabajados", "dias_ausencias", "dias_permisos", "horas_no_trabajadas", "updated_at"])

        if dry_run:
            transaction.set_rollback(True)

    return rows
