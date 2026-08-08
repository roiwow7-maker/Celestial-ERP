from __future__ import annotations

from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db.models import Count

from DATA_scope.models import Employee

from .models import AttendanceRecord


def period_bounds(year: int, month: int) -> tuple[date, date]:
    return date(year, month, 1), date(year, month, monthrange(year, month)[1])


def attendance_summary(records=None) -> dict[str, object]:
    qs = records if records is not None else AttendanceRecord.objects.all()
    rows = list(qs.select_related("employee"))
    total_minutes = sum(record.worked_minutes for record in rows)
    return {
        "records": len(rows),
        "employees": len({record.employee_id for record in rows}),
        "worked_hours": (Decimal(total_minutes) / Decimal("60")).quantize(Decimal("0.01")),
        "present": sum(1 for record in rows if record.status == AttendanceRecord.STATUS_PRESENT),
        "late": sum(1 for record in rows if record.status == AttendanceRecord.STATUS_LATE),
        "absent": sum(1 for record in rows if record.status == AttendanceRecord.STATUS_ABSENT),
        "leave": sum(1 for record in rows if record.status == AttendanceRecord.STATUS_LEAVE),
    }


def monthly_employee_rows(year: int, month: int):
    start, end = period_bounds(year, month)
    records = AttendanceRecord.objects.filter(date__range=(start, end)).select_related("employee")
    grouped = {}
    for record in records:
        row = grouped.setdefault(
            record.employee_id,
            {
                "employee": record.employee,
                "days": 0,
                "worked_minutes": 0,
                "present": 0,
                "late": 0,
                "absent": 0,
                "leave": 0,
            },
        )
        row["days"] += 1
        row["worked_minutes"] += record.worked_minutes
        if record.status == AttendanceRecord.STATUS_PRESENT:
            row["present"] += 1
        elif record.status == AttendanceRecord.STATUS_LATE:
            row["late"] += 1
        elif record.status == AttendanceRecord.STATUS_ABSENT:
            row["absent"] += 1
        elif record.status == AttendanceRecord.STATUS_LEAVE:
            row["leave"] += 1

    rows = []
    for row in grouped.values():
        row["worked_hours"] = (Decimal(row["worked_minutes"]) / Decimal("60")).quantize(Decimal("0.01"))
        rows.append(row)
    return sorted(rows, key=lambda item: item["employee"].nombre)


def attendance_status_rows(records=None):
    qs = records if records is not None else AttendanceRecord.objects.all()
    return qs.values("status").annotate(total=Count("id")).order_by("status")
