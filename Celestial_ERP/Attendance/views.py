from __future__ import annotations

import csv

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from Applet.access import module_permission_required
from DATA_scope.models import Employee

from .forms import AttendanceRecordForm
from .models import AttendanceRecord
from .services import attendance_status_rows, attendance_summary, monthly_employee_rows, period_bounds


def filtered_records(request):
    records = AttendanceRecord.objects.select_related("employee").all()
    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    date_from = request.GET.get("desde", "").strip()
    date_to = request.GET.get("hasta", "").strip()
    if search:
        records = records.filter(
            Q(employee__nombre__icontains=search)
            | Q(employee__rut__icontains=search)
            | Q(employee__codigo_ficha__icontains=search)
        )
    if status:
        records = records.filter(status=status)
    if date_from:
        records = records.filter(date__gte=date_from)
    if date_to:
        records = records.filter(date__lte=date_to)
    return records, {"search": search, "status": status, "date_from": date_from, "date_to": date_to}


@module_permission_required("Attendance.access_attendance_module")
def dashboard(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    month_records = AttendanceRecord.objects.filter(date__gte=month_start, date__lte=today)
    recent = AttendanceRecord.objects.select_related("employee").order_by("-date", "employee__nombre")[:12]
    return render(
        request,
        "Attendance/dashboard.html",
        {
            "summary": attendance_summary(month_records),
            "status_rows": attendance_status_rows(month_records),
            "recent_records": recent,
            "today": today,
        },
    )


@module_permission_required("Attendance.access_attendance_module")
def records(request):
    records_qs, filters = filtered_records(request)
    return render(
        request,
        "Attendance/records.html",
        {
            "records": records_qs[:500],
            "summary": attendance_summary(records_qs),
            "status_choices": AttendanceRecord.STATUS_CHOICES,
            **filters,
        },
    )


@module_permission_required("Attendance.manage_attendance_records")
def record_create(request):
    return attendance_form_view(request, AttendanceRecordForm, "Nuevo registro de asistencia", "attendance:records")


@module_permission_required("Attendance.manage_attendance_records")
def record_update(request, record_id: int):
    record = get_object_or_404(AttendanceRecord, pk=record_id)
    return attendance_form_view(request, AttendanceRecordForm, "Editar registro de asistencia", "attendance:records", instance=record)


@module_permission_required("Attendance.access_attendance_module")
def employee_attendance(request, employee_id: int):
    employee = get_object_or_404(Employee, pk=employee_id)
    records_qs = AttendanceRecord.objects.filter(employee=employee).select_related("employee")
    date_from = request.GET.get("desde", "").strip()
    date_to = request.GET.get("hasta", "").strip()
    if date_from:
        records_qs = records_qs.filter(date__gte=date_from)
    if date_to:
        records_qs = records_qs.filter(date__lte=date_to)
    return render(
        request,
        "Attendance/employee_detail.html",
        {
            "employee": employee,
            "records": records_qs,
            "summary": attendance_summary(records_qs),
            "date_from": date_from,
            "date_to": date_to,
        },
    )


@module_permission_required("Attendance.view_attendance_reports")
def monthly_report(request):
    today = timezone.localdate()
    try:
        year = int(request.GET.get("year") or today.year)
        month = int(request.GET.get("month") or today.month)
        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        year = today.year
        month = today.month
    start, end = period_bounds(year, month)
    records_qs = AttendanceRecord.objects.filter(date__range=(start, end)).select_related("employee")
    return render(
        request,
        "Attendance/monthly_report.html",
        {
            "year": year,
            "month": month,
            "start": start,
            "end": end,
            "summary": attendance_summary(records_qs),
            "rows": monthly_employee_rows(year, month),
        },
    )


@module_permission_required("Attendance.export_attendance_reports")
def export_csv(request):
    records_qs, _ = filtered_records(request)
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="asistencia.csv"'
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(["Fecha", "Codigo ficha", "RUT", "Trabajador", "Departamento", "Entrada", "Salida", "Descanso minutos", "Horas", "Estado", "Fuente", "Notas"])
    for record in records_qs:
        writer.writerow(
            [
                record.date,
                record.employee.codigo_ficha,
                record.employee.rut,
                record.employee.nombre,
                record.employee.division,
                record.check_in or "",
                record.check_out or "",
                record.break_minutes,
                record.worked_hours,
                record.get_status_display(),
                record.get_source_display(),
                record.notes,
            ]
        )
    return response


def attendance_form_view(request, form_class, title: str, back_url: str, instance=None):
    initial = {"date": timezone.localdate()}
    form = form_class(request.POST or None, instance=instance, initial=initial)
    if request.method == "POST" and form.is_valid():
        record = form.save(commit=False)
        record.created_by = request.user if request.user.is_authenticated else None
        record.save()
        messages.success(request, "Registro guardado.")
        return redirect(back_url)
    return render(request, "Attendance/model_form.html", {"form": form, "title": title, "back_url": back_url})
