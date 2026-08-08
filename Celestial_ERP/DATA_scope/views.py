import csv
import json
import subprocess
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import get_valid_filename

from Applet.access import module_permission_required
from Applet.audit import log_event

from .audit import log_manual_change, snapshot
from .forms import EmployeeForm, PayrollEntryForm, PayrollItemForm, PayrollPeriodForm, PayrollSummaryForm
from .models import Employee, ImportRun, PayrollEntry, PayrollItem, PayrollPeriod, PayrollSummary
from .quality import validate_transformed_csv, write_quality_report


UPLOAD_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def require_perm(request, permission: str) -> None:
    if not request.user.has_perm(permission):
        raise PermissionDenied


def decimal_value(value):
    return value or Decimal("0")


def format_money(value):
    return f"{int(decimal_value(value)):,}".replace(",", ".")


def format_decimal(value):
    return f"{decimal_value(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_decimal_filter(value: str) -> Decimal | None:
    text = value.strip().replace(".", "").replace(",", ".")
    if not text:
        return None
    try:
        return Decimal(text)
    except Exception:
        return None


def selected_periods(request):
    period_from = request.GET.get("desde", "").strip()
    period_to = request.GET.get("hasta", "").strip()
    periods = PayrollPeriod.objects.order_by("periodo")
    if period_from:
        periods = periods.filter(periodo__gte=period_from)
    if period_to:
        periods = periods.filter(periodo__lte=period_to)
    return periods, period_from, period_to


def build_report_context(request):
    periods, period_from, period_to = selected_periods(request)
    period_ids = list(periods.values_list("id", flat=True))
    division = request.GET.get("division", "").strip()
    search = request.GET.get("q", "").strip()
    category = request.GET.get("categoria", "").strip()
    liquid_min_raw = request.GET.get("liquido_min", "").strip()
    liquid_max_raw = request.GET.get("liquido_max", "").strip()
    liquid_min = parse_decimal_filter(liquid_min_raw)
    liquid_max = parse_decimal_filter(liquid_max_raw)

    summaries = PayrollSummary.objects.filter(period_id__in=period_ids)
    entries = PayrollEntry.objects.filter(period_id__in=period_ids)

    employee_filter = Q()
    if division:
        employee_filter &= Q(employee__division=division)
    if search:
        employee_filter &= (
            Q(employee__nombre__icontains=search)
            | Q(employee__rut__icontains=search)
            | Q(employee__codigo_ficha__icontains=search)
            | Q(document_number__icontains=search)
        )
    if employee_filter:
        summaries = summaries.filter(employee_filter)
        entry_employee_filter = Q()
        if division:
            entry_employee_filter &= Q(employee__division=division)
        if search:
            entry_employee_filter &= (
                Q(employee__nombre__icontains=search)
                | Q(employee__rut__icontains=search)
                | Q(employee__codigo_ficha__icontains=search)
            )
        entries = entries.filter(entry_employee_filter)
    if liquid_min is not None:
        summaries = summaries.filter(sueldo_liquido__gte=liquid_min)
    if liquid_max is not None:
        summaries = summaries.filter(sueldo_liquido__lte=liquid_max)
    if liquid_min is not None or liquid_max is not None:
        entries = entries.filter(employee_id__in=summaries.values("employee_id"))
    if category:
        entries = entries.filter(item__categoria=category)

    totals = summaries.aggregate(
        liquidaciones=Count("id"),
        trabajadores=Count("employee", distinct=True),
        haberes=Sum("total_haberes_imponibles"),
        haberes_no_imponibles=Sum("total_haberes_no_imponibles"),
        descuentos_legales=Sum("total_descuentos_legales"),
        otros_descuentos=Sum("total_otros_descuentos"),
        liquido=Sum("sueldo_liquido"),
        costo_empresa=Sum("costo_empresa"),
    )

    category_rows = list(
        entries.values("item__categoria")
        .annotate(total=Sum("monto"), movimientos=Count("id"))
        .order_by("-total")
    )
    max_category_total = max((abs(decimal_value(row["total"])) for row in category_rows), default=Decimal("1"))
    category_labels = dict(PayrollItem.CATEGORY_CHOICES)
    for row in category_rows:
        row["label"] = category_labels.get(row["item__categoria"], row["item__categoria"])
        row["display_total"] = format_money(row["total"])
        row["bar_width"] = int((abs(decimal_value(row["total"])) / max_category_total) * 100)

    period_rows = list(
        summaries.values("period__periodo")
        .annotate(
            liquidaciones=Count("id"),
            trabajadores=Count("employee", distinct=True),
            haberes=Sum("total_haberes_imponibles"),
            descuentos=Sum("total_descuentos_legales"),
            liquido=Sum("sueldo_liquido"),
            costo_empresa=Sum("costo_empresa"),
        )
        .order_by("period__periodo")
    )
    max_period_liquido = max((decimal_value(row["liquido"]) for row in period_rows), default=Decimal("1"))
    for row in period_rows:
        row["display_haberes"] = format_money(row["haberes"])
        row["display_descuentos"] = format_money(row["descuentos"])
        row["display_liquido"] = format_money(row["liquido"])
        row["display_costo_empresa"] = format_money(row["costo_empresa"])
        row["bar_height"] = int((decimal_value(row["liquido"]) / max_period_liquido) * 108) if max_period_liquido else 0

    department_rows = list(
        summaries.values("employee__division")
        .annotate(
            liquidaciones=Count("id"),
            trabajadores=Count("employee", distinct=True),
            dias_trabajados=Sum("dias_trabajados"),
            dias_licencias=Sum("dias_licencias"),
            dias_ausencias=Sum("dias_ausencias"),
            horas_extras=Sum("horas_extras"),
            horas_no_trabajadas=Sum("horas_no_trabajadas"),
            liquido=Sum("sueldo_liquido"),
            costo_empresa=Sum("costo_empresa"),
        )
        .order_by("-liquido")
    )
    max_department_liquido = max((decimal_value(row["liquido"]) for row in department_rows), default=Decimal("1"))
    for row in department_rows:
        row["department"] = row["employee__division"] or "Sin departamento"
        row["display_dias_trabajados"] = format_money(row["dias_trabajados"])
        row["display_dias_licencias"] = format_money(row["dias_licencias"])
        row["display_dias_ausencias"] = format_money(row["dias_ausencias"])
        row["display_horas_extras"] = format_decimal(row["horas_extras"])
        row["display_horas_no_trabajadas"] = format_decimal(row["horas_no_trabajadas"])
        row["display_liquido"] = format_money(row["liquido"])
        row["display_costo_empresa"] = format_money(row["costo_empresa"])
        row["bar_width"] = int((decimal_value(row["liquido"]) / max_department_liquido) * 100) if max_department_liquido else 0

    employee_rows = list(
        summaries.values("employee__codigo_ficha", "employee__rut", "employee__nombre", "employee__division")
        .annotate(
            liquidaciones=Count("id"),
            dias_trabajados=Sum("dias_trabajados"),
            horas_extras=Sum("horas_extras"),
            liquido=Sum("sueldo_liquido"),
            costo_empresa=Sum("costo_empresa"),
        )
        .order_by("employee__nombre")[:100]
    )
    for row in employee_rows:
        row["display_dias_trabajados"] = format_money(row["dias_trabajados"])
        row["display_horas_extras"] = format_decimal(row["horas_extras"])
        row["display_liquido"] = format_money(row["liquido"])
        row["display_costo_empresa"] = format_money(row["costo_empresa"])

    all_periods = PayrollPeriod.objects.order_by("-periodo")
    divisions = (
        Employee.objects.exclude(division="")
        .values_list("division", flat=True)
        .distinct()
        .order_by("division")
    )
    return {
        "all_periods": all_periods,
        "divisions": divisions,
        "category_choices": PayrollItem.CATEGORY_CHOICES,
        "period_from": period_from,
        "period_to": period_to,
        "selected_division": division,
        "selected_category": category,
        "search": search,
        "liquid_min": liquid_min_raw,
        "liquid_max": liquid_max_raw,
        "query_string": request.GET.urlencode(),
        "period_count": len(period_ids),
        "totals": totals,
        "category_rows": category_rows,
        "period_rows": period_rows,
        "department_rows": department_rows,
        "employee_rows": employee_rows,
        "display_haberes": format_money(totals["haberes"]),
        "display_haberes_no_imponibles": format_money(totals["haberes_no_imponibles"]),
        "display_descuentos_legales": format_money(totals["descuentos_legales"]),
        "display_otros_descuentos": format_money(totals["otros_descuentos"]),
        "display_liquido": format_money(totals["liquido"]),
        "display_costo_empresa": format_money(totals["costo_empresa"]),
    }


@module_permission_required("DATA_scope.access_payroll_module")
def dashboard(request):
    log_event(request, "dashboard_access", "DATA_scope", "Acceso al dashboard de remuneraciones.")
    latest_periods = (
        PayrollPeriod.objects.annotate(summary_count=Count("payroll_summaries"))
        .order_by("-periodo")[:12]
    )
    employee_status_rows = list(Employee.objects.values("estado").annotate(total=Count("id")).order_by("estado"))
    employee_status_labels = dict(Employee.STATUS_CHOICES)
    for row in employee_status_rows:
        row["label"] = employee_status_labels.get(row["estado"], row["estado"])
    totals_by_category = (
        PayrollEntry.objects.values("item__categoria")
        .annotate(total=Sum("monto"), entries=Count("id"))
        .order_by("item__categoria")
    )
    context = {
        "employee_count": Employee.objects.count(),
        "employee_status_rows": employee_status_rows,
        "period_count": PayrollPeriod.objects.count(),
        "item_count": PayrollItem.objects.count(),
        "entry_count": PayrollEntry.objects.count(),
        "summary_count": PayrollSummary.objects.count(),
        "latest_periods": latest_periods,
        "totals_by_category": totals_by_category,
        "latest_imports": ImportRun.objects.order_by("-created_at")[:5],
    }
    return render(request, "DATA_scope/dashboard.html", context)


@module_permission_required("DATA_scope.access_payroll_module")
def reports(request):
    log_event(request, "report_view", "DATA_scope", "Visualizacion de reportes de remuneraciones.")
    return render(request, "DATA_scope/reports.html", build_report_context(request))


@module_permission_required("DATA_scope.access_payroll_module")
def employees(request):
    status = request.GET.get("estado", "").strip()
    search = request.GET.get("q", "").strip()
    employees_query = Employee.objects.order_by("nombre", "codigo_ficha")
    if status:
        employees_query = employees_query.filter(estado=status)
    if search:
        employees_query = employees_query.filter(
            Q(nombre__icontains=search) | Q(rut__icontains=search) | Q(codigo_ficha__icontains=search)
        )
    status_rows = (
        Employee.objects.values("estado")
        .annotate(total=Count("id"))
        .order_by("estado")
    )
    status_labels = dict(Employee.STATUS_CHOICES)
    for row in status_rows:
        row["label"] = status_labels.get(row["estado"], row["estado"])
    return render(
        request,
        "DATA_scope/employees.html",
        {
            "employees": employees_query[:200],
            "status_choices": Employee.STATUS_CHOICES,
            "selected_status": status,
            "search": search,
            "status_rows": status_rows,
            "can_manage_status": request.user.has_perm("DATA_scope.manage_employee_status"),
        },
    )


@module_permission_required("DATA_scope.access_payroll_module")
def employee_create(request):
    require_perm(request, "DATA_scope.add_employee")
    form = EmployeeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        employee = form.save()
        log_manual_change(request, "employee_created", employee)
        messages.success(request, "Trabajador creado.")
        return redirect("data_scope:employee_detail", employee_id=employee.id)
    return render(
        request,
        "DATA_scope/model_form.html",
        {
            "title": "Nuevo trabajador",
            "form": form,
            "back_url": reverse("data_scope:employees"),
        },
    )


@module_permission_required("DATA_scope.access_payroll_module")
def employee_update(request, employee_id: int):
    require_perm(request, "DATA_scope.change_employee")
    employee = get_object_or_404(Employee, pk=employee_id)
    before = snapshot(employee, fields=list(EmployeeForm.Meta.fields))
    form = EmployeeForm(request.POST or None, instance=employee)
    if request.method == "POST" and form.is_valid():
        employee = form.save()
        log_manual_change(request, "employee_updated", employee, before)
        messages.success(request, "Trabajador actualizado.")
        return redirect("data_scope:employee_detail", employee_id=employee.id)
    return render(
        request,
        "DATA_scope/model_form.html",
        {
            "title": "Editar trabajador",
            "form": form,
            "back_url": reverse("data_scope:employee_detail", kwargs={"employee_id": employee.id}),
        },
    )


@module_permission_required("DATA_scope.access_payroll_module")
def employee_detail(request, employee_id: int):
    employee = get_object_or_404(Employee, pk=employee_id)
    if request.method == "POST":
        if not request.user.has_perm("DATA_scope.manage_employee_status"):
            raise PermissionDenied
        new_status = request.POST.get("estado", "").strip()
        valid_statuses = {value for value, _label in Employee.STATUS_CHOICES}
        if new_status not in valid_statuses:
            messages.error(request, "Estado no valido.")
        elif employee.estado != new_status:
            old_status = employee.get_estado_display()
            employee.estado = new_status
            employee.save(update_fields=["estado", "updated_at"])
            log_event(
                request,
                "employee_status_changed",
                "DATA_scope",
                f"{employee.codigo_ficha}: {old_status} -> {employee.get_estado_display()}",
                object_type="DATA_scope.employee",
                object_id=employee.pk,
                object_repr=str(employee),
                changes={"estado": {"old": old_status, "new": employee.get_estado_display()}},
            )
            messages.success(request, "Estado actualizado.")
        return redirect("data_scope:employee_detail", employee_id=employee.id)

    summaries = (
        PayrollSummary.objects.filter(employee=employee)
        .select_related("period")
        .order_by("-period__periodo")[:24]
    )
    return render(
        request,
        "DATA_scope/employee_detail.html",
        {
            "employee": employee,
            "summaries": summaries,
            "status_choices": Employee.STATUS_CHOICES,
            "can_manage_status": request.user.has_perm("DATA_scope.manage_employee_status"),
        },
    )


@module_permission_required("DATA_scope.access_payroll_module")
def periods(request):
    search = request.GET.get("q", "").strip()
    queryset = PayrollPeriod.objects.annotate(summary_count=Count("payroll_summaries")).order_by("-periodo")
    if search:
        queryset = queryset.filter(periodo__icontains=search)
    return render(
        request,
        "DATA_scope/periods.html",
        {
            "periods": queryset[:200],
            "search": search,
            "can_add": request.user.has_perm("DATA_scope.add_payrollperiod"),
        },
    )


@module_permission_required("DATA_scope.access_payroll_module")
def period_create(request):
    require_perm(request, "DATA_scope.add_payrollperiod")
    form = PayrollPeriodForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        period = form.save()
        log_manual_change(request, "period_created", period)
        messages.success(request, "Periodo creado.")
        return redirect("data_scope:periods")
    return render(request, "DATA_scope/model_form.html", {"title": "Nuevo periodo", "form": form, "back_url": reverse("data_scope:periods")})


@module_permission_required("DATA_scope.access_payroll_module")
def period_update(request, period_id: int):
    require_perm(request, "DATA_scope.change_payrollperiod")
    period = get_object_or_404(PayrollPeriod, pk=period_id)
    before = snapshot(period, fields=PayrollPeriodForm.Meta.fields)
    form = PayrollPeriodForm(request.POST or None, instance=period)
    if request.method == "POST" and form.is_valid():
        period = form.save()
        log_manual_change(request, "period_updated", period, before)
        messages.success(request, "Periodo actualizado.")
        return redirect("data_scope:periods")
    return render(request, "DATA_scope/model_form.html", {"title": "Editar periodo", "form": form, "back_url": reverse("data_scope:periods")})


@module_permission_required("DATA_scope.access_payroll_module")
def items(request):
    search = request.GET.get("q", "").strip()
    category = request.GET.get("categoria", "").strip()
    queryset = PayrollItem.objects.order_by("categoria", "codigo")
    if search:
        queryset = queryset.filter(Q(codigo__icontains=search) | Q(descripcion__icontains=search))
    if category:
        queryset = queryset.filter(categoria=category)
    return render(
        request,
        "DATA_scope/items.html",
        {
            "items": queryset[:300],
            "search": search,
            "selected_category": category,
            "category_choices": PayrollItem.CATEGORY_CHOICES,
            "can_add": request.user.has_perm("DATA_scope.add_payrollitem"),
        },
    )


@module_permission_required("DATA_scope.access_payroll_module")
def item_create(request):
    require_perm(request, "DATA_scope.add_payrollitem")
    form = PayrollItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save()
        log_manual_change(request, "item_created", item)
        messages.success(request, "Item creado.")
        return redirect("data_scope:items")
    return render(request, "DATA_scope/model_form.html", {"title": "Nuevo item", "form": form, "back_url": reverse("data_scope:items")})


@module_permission_required("DATA_scope.access_payroll_module")
def item_update(request, item_id: int):
    require_perm(request, "DATA_scope.change_payrollitem")
    item = get_object_or_404(PayrollItem, pk=item_id)
    before = snapshot(item, fields=PayrollItemForm.Meta.fields)
    form = PayrollItemForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        item = form.save()
        log_manual_change(request, "item_updated", item, before)
        messages.success(request, "Item actualizado.")
        return redirect("data_scope:items")
    return render(request, "DATA_scope/model_form.html", {"title": "Editar item", "form": form, "back_url": reverse("data_scope:items")})


@module_permission_required("DATA_scope.access_payroll_module")
def summaries(request):
    search = request.GET.get("q", "").strip()
    period = request.GET.get("periodo", "").strip()
    queryset = PayrollSummary.objects.select_related("employee", "period").order_by("-period__periodo", "employee__codigo_ficha")
    if search:
        queryset = queryset.filter(
            Q(document_number__icontains=search)
            | Q(employee__codigo_ficha__icontains=search)
            | Q(employee__rut__icontains=search)
            | Q(employee__nombre__icontains=search)
        )
    if period:
        queryset = queryset.filter(period__periodo=period)
    return render(
        request,
        "DATA_scope/summaries.html",
        {
            "summaries": queryset[:200],
            "search": search,
            "selected_period": period,
            "periods": PayrollPeriod.objects.order_by("-periodo")[:120],
            "can_add": request.user.has_perm("DATA_scope.add_payrollsummary"),
        },
    )


@module_permission_required("DATA_scope.access_payroll_module")
def summary_detail(request, summary_id: int):
    summary = get_object_or_404(PayrollSummary.objects.select_related("employee", "period"), pk=summary_id)
    entries = PayrollEntry.objects.select_related("item").filter(employee=summary.employee, period=summary.period).order_by("item__categoria", "item__codigo")
    return render(
        request,
        "DATA_scope/summary_detail.html",
        {
            "summary": summary,
            "entries": entries,
            "can_change": request.user.has_perm("DATA_scope.change_payrollsummary"),
            "can_add_entry": request.user.has_perm("DATA_scope.add_payrollentry"),
        },
    )


@module_permission_required("DATA_scope.access_payroll_module")
def summary_create(request):
    require_perm(request, "DATA_scope.add_payrollsummary")
    form = PayrollSummaryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        summary = form.save()
        log_manual_change(request, "summary_created", summary)
        messages.success(request, "Liquidacion creada.")
        return redirect("data_scope:summary_detail", summary_id=summary.id)
    return render(request, "DATA_scope/model_form.html", {"title": "Nueva liquidacion", "form": form, "back_url": reverse("data_scope:summaries")})


@module_permission_required("DATA_scope.access_payroll_module")
def summary_update(request, summary_id: int):
    require_perm(request, "DATA_scope.change_payrollsummary")
    summary = get_object_or_404(PayrollSummary, pk=summary_id)
    before = snapshot(summary, fields=PayrollSummaryForm.Meta.fields)
    form = PayrollSummaryForm(request.POST or None, instance=summary)
    if request.method == "POST" and form.is_valid():
        summary = form.save()
        log_manual_change(request, "summary_updated", summary, before)
        messages.success(request, "Liquidacion actualizada.")
        return redirect("data_scope:summary_detail", summary_id=summary.id)
    return render(
        request,
        "DATA_scope/model_form.html",
        {
            "title": "Editar liquidacion",
            "form": form,
            "back_url": reverse("data_scope:summary_detail", kwargs={"summary_id": summary.id}),
        },
    )


@module_permission_required("DATA_scope.access_payroll_module")
def entries(request):
    search = request.GET.get("q", "").strip()
    period = request.GET.get("periodo", "").strip()
    queryset = PayrollEntry.objects.select_related("employee", "period", "item").order_by("-period__periodo", "employee__codigo_ficha", "item__codigo")
    if search:
        queryset = queryset.filter(
            Q(employee__codigo_ficha__icontains=search)
            | Q(employee__rut__icontains=search)
            | Q(employee__nombre__icontains=search)
            | Q(item__codigo__icontains=search)
            | Q(item__descripcion__icontains=search)
        )
    if period:
        queryset = queryset.filter(period__periodo=period)
    return render(
        request,
        "DATA_scope/entries.html",
        {
            "entries": queryset[:300],
            "search": search,
            "selected_period": period,
            "periods": PayrollPeriod.objects.order_by("-periodo")[:120],
            "can_add": request.user.has_perm("DATA_scope.add_payrollentry"),
        },
    )


@module_permission_required("DATA_scope.access_payroll_module")
def entry_create(request):
    require_perm(request, "DATA_scope.add_payrollentry")
    form = PayrollEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save()
        log_manual_change(request, "entry_created", entry)
        messages.success(request, "Movimiento creado.")
        return redirect("data_scope:entries")
    return render(request, "DATA_scope/model_form.html", {"title": "Nuevo movimiento", "form": form, "back_url": reverse("data_scope:entries")})


@module_permission_required("DATA_scope.access_payroll_module")
def entry_update(request, entry_id: int):
    require_perm(request, "DATA_scope.change_payrollentry")
    entry = get_object_or_404(PayrollEntry, pk=entry_id)
    before = snapshot(entry, fields=PayrollEntryForm.Meta.fields)
    form = PayrollEntryForm(request.POST or None, instance=entry)
    if request.method == "POST" and form.is_valid():
        entry = form.save()
        log_manual_change(request, "entry_updated", entry, before)
        messages.success(request, "Movimiento actualizado.")
        return redirect("data_scope:entries")
    return render(request, "DATA_scope/model_form.html", {"title": "Editar movimiento", "form": form, "back_url": reverse("data_scope:entries")})


@module_permission_required("DATA_scope.access_payroll_module")
def kanban(request):
    return render(request, "DATA_scope/kanban.html")


@module_permission_required("DATA_scope.access_payroll_module")
def export_reports_csv(request):
    if not request.user.has_perm("DATA_scope.download_upload_output"):
        raise PermissionDenied
    log_event(request, "report_export_csv", "DATA_scope", "Exportacion CSV de reportes de remuneraciones.")
    context = build_report_context(request)
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="reporte_remuneraciones.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Reporte por periodo"])
    writer.writerow(["Periodo", "Liquidaciones", "Trabajadores", "Haberes imponibles", "Descuentos legales", "Liquido", "Costo empresa"])
    for row in context["period_rows"]:
        writer.writerow([
            row["period__periodo"],
            row["liquidaciones"],
            row["trabajadores"],
            int(decimal_value(row["haberes"])),
            int(decimal_value(row["descuentos"])),
            int(decimal_value(row["liquido"])),
            int(decimal_value(row["costo_empresa"])),
        ])
    writer.writerow([])
    writer.writerow(["Reporte por departamento"])
    writer.writerow(["Departamento", "Liquidaciones", "Trabajadores", "Dias trabajados", "Horas extras", "Horas no trabajadas", "Liquido", "Costo empresa"])
    for row in context["department_rows"]:
        writer.writerow([
            row["department"],
            row["liquidaciones"],
            row["trabajadores"],
            int(decimal_value(row["dias_trabajados"])),
            str(decimal_value(row["horas_extras"])).replace(".", ","),
            str(decimal_value(row["horas_no_trabajadas"])).replace(".", ","),
            int(decimal_value(row["liquido"])),
            int(decimal_value(row["costo_empresa"])),
        ])
    writer.writerow([])
    writer.writerow(["Reporte por trabajador"])
    writer.writerow(["Codigo", "RUT", "Nombre", "Departamento", "Liquidaciones", "Dias trabajados", "Horas extras", "Liquido", "Costo empresa"])
    for row in context["employee_rows"]:
        writer.writerow([
            row["employee__codigo_ficha"],
            row["employee__rut"],
            row["employee__nombre"],
            row["employee__division"],
            row["liquidaciones"],
            int(decimal_value(row["dias_trabajados"])),
            str(decimal_value(row["horas_extras"])).replace(".", ","),
            int(decimal_value(row["liquido"])),
            int(decimal_value(row["costo_empresa"])),
        ])
    return response


@module_permission_required("DATA_scope.download_upload_output")
def export_employee_csv(request, employee_id: int):
    employee = get_object_or_404(Employee, pk=employee_id)
    summaries = PayrollSummary.objects.filter(employee=employee).select_related("period").order_by("period__periodo")
    entries = PayrollEntry.objects.filter(employee=employee).select_related("period", "item").order_by("period__periodo", "item__codigo")
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="trabajador_{employee.codigo_ficha}.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Trabajador", employee.codigo_ficha, employee.rut, employee.nombre, employee.division])
    writer.writerow([])
    writer.writerow(["Liquidaciones"])
    writer.writerow(["Periodo", "Documento", "Sueldo liquido", "Costo empresa", "Haberes imponibles", "Descuentos legales"])
    for summary in summaries:
        writer.writerow([
            summary.period.periodo,
            summary.document_number,
            int(summary.sueldo_liquido),
            int(summary.costo_empresa),
            int(summary.total_haberes_imponibles),
            int(summary.total_descuentos_legales),
        ])
    writer.writerow([])
    writer.writerow(["Movimientos"])
    writer.writerow(["Periodo", "Codigo item", "Categoria", "Descripcion", "Monto"])
    for entry in entries:
        writer.writerow([
            entry.period.periodo,
            entry.item.codigo,
            entry.item.categoria,
            entry.item.descripcion,
            int(entry.monto),
        ])
    log_event(request, "employee_export_csv", "DATA_scope", f"Exportacion trabajador {employee.codigo_ficha}.")
    return response


@module_permission_required("DATA_scope.download_upload_output")
def export_period_csv(request, period_id: int):
    period = get_object_or_404(PayrollPeriod, pk=period_id)
    summaries = PayrollSummary.objects.filter(period=period).select_related("employee").order_by("employee__codigo_ficha")
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="periodo_{period.periodo}.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Periodo", period.periodo, period.year, period.month])
    writer.writerow(["Ficha", "RUT", "Trabajador", "Division", "Documento", "Sueldo liquido", "Costo empresa"])
    for summary in summaries:
        writer.writerow([
            summary.employee.codigo_ficha,
            summary.employee.rut,
            summary.employee.nombre,
            summary.employee.division,
            summary.document_number,
            int(summary.sueldo_liquido),
            int(summary.costo_empresa),
        ])
    log_event(request, "period_export_csv", "DATA_scope", f"Exportacion periodo {period.periodo}.")
    return response


@module_permission_required("DATA_scope.download_upload_output")
def export_summary_csv(request, summary_id: int):
    summary = get_object_or_404(PayrollSummary.objects.select_related("employee", "period"), pk=summary_id)
    entries = PayrollEntry.objects.filter(employee=summary.employee, period=summary.period).select_related("item").order_by("item__categoria", "item__codigo")
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="liquidacion_{summary.document_number}.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Liquidacion", summary.document_number])
    writer.writerow(["Periodo", summary.period.periodo])
    writer.writerow(["Ficha", summary.employee.codigo_ficha])
    writer.writerow(["RUT", summary.employee.rut])
    writer.writerow(["Trabajador", summary.employee.nombre])
    writer.writerow([])
    writer.writerow(["Total", "Valor"])
    for label, value in [
        ("Sueldo base", summary.sueldo_base),
        ("Haberes imponibles", summary.total_haberes_imponibles),
        ("Haberes no imponibles", summary.total_haberes_no_imponibles),
        ("Descuentos legales", summary.total_descuentos_legales),
        ("Otros descuentos", summary.total_otros_descuentos),
        ("Sueldo liquido", summary.sueldo_liquido),
        ("Costo empresa", summary.costo_empresa),
    ]:
        writer.writerow([label, int(value)])
    writer.writerow([])
    writer.writerow(["Movimientos"])
    writer.writerow(["Codigo item", "Categoria", "Descripcion", "Monto"])
    for entry in entries:
        writer.writerow([entry.item.codigo, entry.item.categoria, entry.item.descripcion, int(entry.monto)])
    log_event(request, "summary_export_csv", "DATA_scope", f"Exportacion liquidacion {summary.document_number}.")
    return response


@module_permission_required("DATA_scope.upload_payroll_data")
def upload_data(request):
    context = {
        "latest_imports": ImportRun.objects.order_by("-created_at")[:5],
        "processed": False,
        "can_import": request.user.has_perm("DATA_scope.import_payroll_data"),
        "can_clear": request.user.has_perm("DATA_scope.clear_payroll_data"),
    }
    if request.method != "POST":
        return render(request, "DATA_scope/upload.html", context)

    load_scope = request.POST.get("load_scope", "massive")
    individual_employee = request.POST.get("codigo_ficha", "").strip()
    wants_import = request.POST.get("importar_erp") == "on"
    wants_clear = request.POST.get("limpiar_datos") == "on"

    if load_scope == "individual" and not individual_employee:
        context["error"] = "Para carga individual debes indicar el codigo de ficha."
        return render(request, "DATA_scope/upload.html", context)
    if wants_import and not request.user.has_perm("DATA_scope.import_payroll_data"):
        raise PermissionDenied
    if wants_clear and not request.user.has_perm("DATA_scope.clear_payroll_data"):
        raise PermissionDenied

    uploaded_file = request.FILES.get("archivo")
    if not uploaded_file:
        log_event(request, "upload_error", "DATA_scope", "Intento de carga sin archivo seleccionado.")
        context["error"] = "Debes seleccionar un archivo."
        return render(request, "DATA_scope/upload.html", context)

    original_name = get_valid_filename(uploaded_file.name)
    suffix = Path(original_name).suffix.lower()
    if suffix not in UPLOAD_EXTENSIONS:
        log_event(request, "upload_error", "DATA_scope", f"Formato no soportado: {original_name}")
        context["error"] = "Formato no soportado. Usa CSV, XLSX o XLS."
        return render(request, "DATA_scope/upload.html", context)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    upload_dir = settings.PROJECT_ROOT / "uploads" / run_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    input_path = upload_dir / original_name
    with input_path.open("wb") as handle:
        for chunk in uploaded_file.chunks():
            handle.write(chunk)

    transformed_path = upload_dir / "transformed.csv"
    category_dir = upload_dir / "csv_por_categoria"
    equivalent_dir = upload_dir / "csv_equivalentes_liquidaciones"
    excel_path = upload_dir / "Liquidaciones_Historicas_Cargadas.xlsx"

    command = [
        sys.executable,
        str(settings.PROJECT_ROOT / "run_etl.py"),
        "--input",
        str(input_path),
        "--source-format",
        request.POST.get("source_format", "auto"),
        "--transformed-output",
        str(transformed_path),
        "--category-output-dir",
        str(category_dir),
        "--equivalent-output-dir",
        str(equivalent_dir),
        "--excel-output",
        str(excel_path),
        "--rut-empresa",
        request.POST.get("rut_empresa", "").strip(),
    ]
    if request.POST.get("generar_excel") != "on":
        command.append("--skip-excel")
    if not wants_import:
        command.append("--skip-import")
    if wants_clear:
        command.append("--clear")

    download_candidates = [
        ("CSV transformado", str(transformed_path)),
        ("Resumen generacion", str(equivalent_dir / "resumen_generacion.csv")),
        ("Reporte calidad carga", str(upload_dir / "reporte_calidad_carga.csv")),
        ("Liquidaciones CSV", str(equivalent_dir / "Liquidaciones.csv")),
        ("Excel generado", str(excel_path)),
    ]

    if request.POST.get("procesar_async", "on") == "on":
        job_config = {
            "run_id": run_id,
            "input_name": original_name,
            "upload_dir": str(upload_dir),
            "project_root": str(settings.PROJECT_ROOT),
            "command": command,
            "transformed_path": str(transformed_path),
            "download_candidates": download_candidates,
            "timeout_seconds": 1800,
        }
        job_config_path = upload_dir / "job_config.json"
        job_config_path.write_text(json.dumps(job_config, ensure_ascii=False, indent=2), encoding="utf-8")
        (upload_dir / "job_status.json").write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "status": "queued",
                    "input_name": original_name,
                    "return_code": None,
                    "quality_issue_count": 0,
                    "downloads": [],
                    "error": "",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.Popen(
            [sys.executable, "manage.py", "run_upload_job", str(job_config_path)],
            cwd=settings.BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        log_event(request, "upload_queued", "DATA_scope", f"Carga ETL en segundo plano: {original_name}")
        context.update(
            {
                "run_id": run_id,
                "input_name": original_name,
                "job_started": True,
                "processed": True,
                "success": True,
                "status_url": reverse("data_scope:upload_status", kwargs={"run_id": run_id}),
            }
        )
        return render(request, "DATA_scope/upload.html", context)

    try:
        log_event(
            request,
            "upload_started",
            "DATA_scope",
            f"Inicio de carga ETL {load_scope}: {original_name} {individual_employee}".strip(),
        )
        completed = subprocess.run(
            command,
            cwd=settings.PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=600,
        )
        return_code = completed.returncode
        stdout = completed.stdout[-12000:]
        stderr = completed.stderr[-12000:]
    except subprocess.TimeoutExpired as exc:
        return_code = 124
        stdout = (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else ""
        stderr = "El proceso ETL supero el tiempo maximo de 10 minutos."
        log_event(request, "upload_timeout", "DATA_scope", f"Tiempo maximo superado en carga ETL: {original_name}")

    if return_code == 0:
        log_event(request, "upload_success", "DATA_scope", f"Carga ETL completada: {original_name}")
    else:
        log_event(request, "upload_failed", "DATA_scope", f"Carga ETL fallo ({return_code}): {original_name}")

    quality_report_path = upload_dir / "reporte_calidad_carga.csv"
    quality_issue_count = 0
    if transformed_path.exists():
        quality_issues = validate_transformed_csv(transformed_path)
        quality_issue_count = len(quality_issues)
        write_quality_report(quality_report_path, quality_issues)
        if quality_issue_count:
            log_event(request, "upload_quality_issues", "DATA_scope", f"{quality_issue_count} observaciones en {original_name}")

    downloads = []
    for label, raw_path in download_candidates:
        path = Path(raw_path)
        if path.exists():
            downloads.append(
                {
                    "label": label,
                    "url": reverse(
                        "data_scope:download_upload_output",
                        kwargs={"run_id": run_id, "relative_path": str(path.relative_to(upload_dir)).replace("\\", "/")},
                    ),
                }
            )

    context.update(
        {
            "run_id": run_id,
            "input_name": original_name,
            "return_code": return_code,
            "stdout": stdout,
            "stderr": stderr,
            "downloads": downloads,
            "success": return_code == 0,
            "processed": True,
            "load_scope": load_scope,
            "individual_employee": individual_employee,
            "quality_issue_count": quality_issue_count,
        }
    )
    return render(request, "DATA_scope/upload.html", context)


@module_permission_required("DATA_scope.upload_payroll_data")
def upload_status(request, run_id: str):
    upload_dir = settings.PROJECT_ROOT / "uploads" / run_id
    status_path = upload_dir / "job_status.json"
    if not status_path.exists():
        raise Http404("Estado de carga no encontrado.")
    status = json.loads(status_path.read_text(encoding="utf-8"))
    downloads = []
    for item in status.get("downloads", []):
        downloads.append(
            {
                "label": item["label"],
                "url": reverse(
                    "data_scope:download_upload_output",
                    kwargs={"run_id": run_id, "relative_path": item["relative_path"]},
                ),
            }
        )
    context = {
        "latest_imports": ImportRun.objects.order_by("-created_at")[:5],
        "processed": True,
        "job_started": status["status"] in {"queued", "running"},
        "run_id": run_id,
        "input_name": status.get("input_name", ""),
        "success": status["status"] != "failed",
        "job_status": status["status"],
        "return_code": status.get("return_code"),
        "quality_issue_count": status.get("quality_issue_count", 0),
        "downloads": downloads,
        "can_import": request.user.has_perm("DATA_scope.import_payroll_data"),
        "can_clear": request.user.has_perm("DATA_scope.clear_payroll_data"),
        "status_url": reverse("data_scope:upload_status", kwargs={"run_id": run_id}),
    }
    return render(request, "DATA_scope/upload.html", context)


@module_permission_required("DATA_scope.download_upload_output")
def download_upload_output(request, run_id: str, relative_path: str):
    base_dir = (settings.PROJECT_ROOT / "uploads" / run_id).resolve()
    target = (base_dir / relative_path).resolve()
    if base_dir not in target.parents and target != base_dir:
        raise Http404("Ruta invalida.")
    if not target.exists() or not target.is_file():
        raise Http404("Archivo no encontrado.")
    return FileResponse(target.open("rb"), as_attachment=True, filename=target.name)


@module_permission_required("DATA_scope.access_payroll_module")
def route_probe(request):
    routes = [
        ("Portal Applet", reverse("applet:home")),
        ("Remuneraciones", reverse("data_scope:payroll_dashboard")),
        ("Trabajadores", reverse("data_scope:employees")),
        ("Kanban", reverse("data_scope:kanban")),
        ("Reportes", reverse("data_scope:reports")),
        ("Exportar reporte CSV", reverse("data_scope:export_reports_csv")),
        ("Cargar datos", reverse("data_scope:upload_data")),
        ("Admin Django", "/admin/"),
    ]
    context = {
        "routes": [
            {
                "name": name,
                "path": path,
                "absolute": request.build_absolute_uri(path),
            }
            for name, path in routes
        ]
    }
    return render(request, "DATA_scope/route_probe.html", context)
