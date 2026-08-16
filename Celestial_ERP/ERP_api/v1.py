import json
import subprocess
import sys
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.utils.text import get_valid_filename

from Accounting.forms import ChartAccountForm, CostCenterForm, PayrollItemAccountMappingForm
from Attendance.forms import AttendanceRecordForm
from Commerce.forms import CustomerForm, PurchaseOrderForm, SalesOrderForm, SupplierForm
from DATA_scope.forms import EmployeeForm, PayrollEntryForm, PayrollItemForm, PayrollPeriodForm, PayrollSummaryForm
from Inventory.forms import ProductForm, StockMovementForm, WarehouseForm
from Inventory.services import apply_stock_movement
from Accounting.models import JournalEntryLine
from Accounting.services import accounting_report_summary
from Attendance.models import AttendanceRecord
from Attendance.services import attendance_status_rows, attendance_summary
from Commerce.models import PurchaseOrder, SalesOrder
from Commerce.services import commerce_summary
from Inventory.models import StockBalance, Warehouse
from Inventory.services import inventory_summary
from Applet.services import ensure_role_groups
from DATA_scope.models import ImportRun, PayrollSummary


RESOURCE_DEFINITIONS = {
    "employees": ("Trabajadores", EmployeeForm, "DATA_scope.access_payroll_module", "DATA_scope"),
    "periods": ("Períodos", PayrollPeriodForm, "DATA_scope.access_payroll_module", "DATA_scope"),
    "payroll-items": ("Ítems de remuneración", PayrollItemForm, "DATA_scope.access_payroll_module", "DATA_scope"),
    "payroll-summaries": ("Liquidaciones", PayrollSummaryForm, "DATA_scope.access_payroll_module", "DATA_scope"),
    "payroll-entries": ("Movimientos de remuneración", PayrollEntryForm, "DATA_scope.access_payroll_module", "DATA_scope"),
    "attendance": ("Registros de asistencia", AttendanceRecordForm, "Attendance.access_attendance_module", "Attendance"),
    "accounts": ("Plan de cuentas", ChartAccountForm, "Accounting.access_accounting_module", "Accounting"),
    "cost-centers": ("Centros de costo", CostCenterForm, "Accounting.access_accounting_module", "Accounting"),
    "account-mappings": ("Mapeos contables", PayrollItemAccountMappingForm, "Accounting.access_accounting_module", "Accounting"),
    "products": ("Productos", ProductForm, "Inventory.access_inventory_module", "Inventory"),
    "warehouses": ("Bodegas", WarehouseForm, "Inventory.access_inventory_module", "Inventory"),
    "stock-movements": ("Movimientos de stock", StockMovementForm, "Inventory.access_inventory_module", "Inventory"),
    "suppliers": ("Proveedores", SupplierForm, "Commerce.access_commerce_module", "Commerce"),
    "customers": ("Clientes", CustomerForm, "Commerce.access_commerce_module", "Commerce"),
    "purchases": ("Órdenes de compra", PurchaseOrderForm, "Commerce.access_commerce_module", "Commerce"),
    "sales": ("Órdenes de venta", SalesOrderForm, "Commerce.access_commerce_module", "Commerce"),
}


def response(data, status=200):
    return JsonResponse(data, status=status, json_dumps_params={"ensure_ascii": False})


def require_user(request):
    if not request.user.is_authenticated:
        raise PermissionDenied


def definition(request, key):
    require_user(request)
    value = RESOURCE_DEFINITIONS.get(key)
    if not value:
        return None
    title, form_class, access_permission, module = value
    if not request.user.has_perm(access_permission):
        raise PermissionDenied
    return title, form_class, module


def scalar(value):
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def json_safe(value):
    if isinstance(value, dict): return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)): return [json_safe(item) for item in value]
    return scalar(value)


def serialize_instance(instance, form_class):
    row = {"id": instance.pk, "label": str(instance)}
    for name in form_class.Meta.fields:
        field = instance._meta.get_field(name)
        value = getattr(instance, name)
        if isinstance(field, models.ForeignKey):
            row[name] = value.pk if value else None
            row[f"{name}_label"] = str(value) if value else ""
        else:
            row[name] = scalar(value)
    return row


def field_schema(name, field):
    widget_type = getattr(field.widget, "input_type", "text")
    result = {
        "name": name,
        "label": field.label,
        "required": field.required,
        "type": widget_type,
        "help_text": str(field.help_text or ""),
    }
    choices = getattr(field, "choices", None)
    if choices:
        result["type"] = "select"
        result["options"] = [{"value": str(value), "label": str(label)} for value, label in choices if value != ""]
    return result


def parse_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


@ensure_csrf_cookie
@require_http_methods(["GET"])
def session_view(request):
    if not request.user.is_authenticated:
        return response({"authenticated": False})
    return response({
        "authenticated": True,
        "user": {"id": request.user.pk, "username": request.user.username, "name": request.user.get_full_name() or request.user.username},
        "permissions": sorted(request.user.get_all_permissions()),
    })


@require_http_methods(["POST"])
def login_view(request):
    data = parse_body(request)
    if data is None:
        return response({"error": "JSON inválido."}, 400)
    user = authenticate(request, username=data.get("username", ""), password=data.get("password", ""))
    if user is None or not user.is_active:
        return response({"error": "Usuario o contraseña incorrectos."}, 400)
    login(request, user)
    return response({
        "authenticated": True,
        "user": {"id": user.pk, "username": user.username, "name": user.get_full_name() or user.username},
        "permissions": sorted(user.get_all_permissions()),
    })


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return response({"ok": True})


@require_http_methods(["GET"])
def catalog(request):
    require_user(request)
    resources = []
    for key, (title, form_class, permission, module) in RESOURCE_DEFINITIONS.items():
        if request.user.has_perm(permission):
            resources.append({"key": key, "title": title, "module": module, "count": form_class.Meta.model.objects.count()})
    return response({"resources": resources})


@require_http_methods(["GET"])
def reports(request):
    require_user(request)
    sections = []
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    selected_status = request.GET.get("status", "")
    if request.user.has_perm("DATA_scope.access_payroll_module"):
        payroll_qs = PayrollSummary.objects.select_related("period", "employee")
        period_from = request.GET.get("period_from", "")
        period_to = request.GET.get("period_to", "")
        division = request.GET.get("division", "")
        if period_from: payroll_qs = payroll_qs.filter(period__periodo__gte=period_from)
        if period_to: payroll_qs = payroll_qs.filter(period__periodo__lte=period_to)
        if division: payroll_qs = payroll_qs.filter(employee__division=division)
        payroll_rows = list(payroll_qs.values("period__periodo").annotate(
            liquidaciones=Count("id"), trabajadores=Count("employee", distinct=True),
            liquido=Sum("sueldo_liquido"), costo_empresa=Sum("costo_empresa"),
        ).order_by("-period__periodo")[:24])
        sections.append({"key": "payroll", "title": "Remuneraciones por período", "summary": {"liquidaciones": payroll_qs.count(), "trabajadores": payroll_qs.values("employee").distinct().count(), "total_liquido": payroll_qs.aggregate(v=Sum("sueldo_liquido"))["v"] or 0, "costo_empresa": payroll_qs.aggregate(v=Sum("costo_empresa"))["v"] or 0}, "columns": ["period__periodo", "liquidaciones", "trabajadores", "liquido", "costo_empresa"], "rows": payroll_rows, "charts": [{"title": "Líquido por período", "series": [{"label": row["period__periodo"], "value": row["liquido"] or 0} for row in reversed(payroll_rows)]}, {"title": "Costo empresa por período", "series": [{"label": row["period__periodo"], "value": row["costo_empresa"] or 0} for row in reversed(payroll_rows)]}], "filters": [{"name": "period_from", "label": "Período desde", "type": "month"}, {"name": "period_to", "label": "Período hasta", "type": "month"}, {"name": "division", "label": "División", "type": "select", "options": list(PayrollSummary.objects.exclude(employee__division="").values_list("employee__division", flat=True).distinct().order_by("employee__division"))}]})
    if request.user.has_perm("Attendance.view_attendance_reports"):
        attendance_qs = AttendanceRecord.objects.all()
        if date_from: attendance_qs = attendance_qs.filter(date__gte=date_from)
        if date_to: attendance_qs = attendance_qs.filter(date__lte=date_to)
        if selected_status: attendance_qs = attendance_qs.filter(status=selected_status)
        rows = list(attendance_status_rows(attendance_qs))
        labels = dict(AttendanceRecord.STATUS_CHOICES)
        for row in rows: row["status_label"] = labels.get(row["status"], row["status"])
        sections.append({"key": "attendance", "title": "Asistencia", "summary": attendance_summary(attendance_qs), "columns": ["status_label", "total"], "rows": rows, "charts": [{"title": "Distribución por estado", "series": [{"label": row["status_label"], "value": row["total"]} for row in rows]}], "filters": [{"name": "date_from", "label": "Fecha desde", "type": "date"}, {"name": "date_to", "label": "Fecha hasta", "type": "date"}, {"name": "status", "label": "Estado", "type": "select", "options": [{"value": key, "label": label} for key, label in AttendanceRecord.STATUS_CHOICES]}]})
    if request.user.has_perm("Accounting.view_accounting_reports"):
        lines = JournalEntryLine.objects.all()
        if date_from: lines = lines.filter(journal_entry__date__gte=date_from)
        if date_to: lines = lines.filter(journal_entry__date__lte=date_to)
        rows = list(lines.values("account__code", "account__name", "account__account_type").annotate(total_debit=Sum("debit"), total_credit=Sum("credit")).order_by("account__code"))
        for row in rows: row["balance"] = (row["total_debit"] or 0) - (row["total_credit"] or 0)
        sections.append({"key": "accounting", "title": "Contabilidad", "summary": {**accounting_report_summary(), "filas_filtradas": lines.count()}, "columns": ["account__code", "account__name", "total_debit", "total_credit", "balance"], "rows": rows, "charts": [{"title": "Debe por cuenta", "series": [{"label": row["account__code"], "value": row["total_debit"] or 0} for row in rows]}, {"title": "Haber por cuenta", "series": [{"label": row["account__code"], "value": row["total_credit"] or 0} for row in rows]}], "filters": [{"name": "date_from", "label": "Fecha desde", "type": "date"}, {"name": "date_to", "label": "Fecha hasta", "type": "date"}]})
    if request.user.has_perm("Inventory.view_inventory_reports"):
        balances = StockBalance.objects.select_related("product", "warehouse")
        warehouse = request.GET.get("warehouse", ""); category = request.GET.get("category", "")
        if warehouse: balances = balances.filter(warehouse_id=warehouse)
        if category: balances = balances.filter(product__category=category)
        rows = [{"sku": item.product.sku, "producto": item.product.name, "categoria": item.product.category, "bodega": item.warehouse.code, "cantidad": item.quantity, "costo_promedio": item.average_cost, "valor": item.total_value} for item in balances[:300]]
        category_rows = list(balances.values("product__category").annotate(valor=Sum(models.F("quantity") * models.F("average_cost"))).order_by("product__category"))
        sections.append({"key": "inventory", "title": "Valorización de inventario", "summary": {**inventory_summary(), "saldos_filtrados": balances.count()}, "columns": ["sku", "producto", "categoria", "bodega", "cantidad", "costo_promedio", "valor"], "rows": rows, "charts": [{"title": "Valor por categoría", "series": [{"label": row["product__category"] or "Sin categoría", "value": row["valor"] or 0} for row in category_rows]}], "filters": [{"name": "warehouse", "label": "Bodega", "type": "select", "options": [{"value": item.id, "label": str(item)} for item in Warehouse.objects.all()]}, {"name": "category", "label": "Categoría", "type": "select", "options": list(StockBalance.objects.exclude(product__category="").values_list("product__category", flat=True).distinct().order_by("product__category"))}]})
    if request.user.has_perm("Commerce.view_commerce_reports"):
        purchases = PurchaseOrder.objects.prefetch_related("lines"); sales = SalesOrder.objects.prefetch_related("lines")
        if date_from: purchases = purchases.filter(date__gte=date_from); sales = sales.filter(date__gte=date_from)
        if date_to: purchases = purchases.filter(date__lte=date_to); sales = sales.filter(date__lte=date_to)
        if selected_status: purchases = purchases.filter(status=selected_status); sales = sales.filter(status=selected_status)
        rows = [{"tipo": "Compra", "numero": row.number, "fecha": row.date, "estado": row.get_status_display(), "tercero": str(row.supplier), "total": row.total_amount} for row in purchases] + [{"tipo": "Venta", "numero": row.number, "fecha": row.date, "estado": row.get_status_display(), "tercero": str(row.customer), "total": row.total_amount} for row in sales]
        sections.append({"key": "commerce", "title": "Actividad comercial", "summary": {**commerce_summary(), "compras_filtradas": purchases.count(), "ventas_filtradas": sales.count()}, "columns": ["tipo", "numero", "fecha", "estado", "tercero", "total"], "rows": rows, "charts": [{"title": "Compras versus ventas", "series": [{"label": "Compras", "value": sum((row.total_amount for row in purchases), Decimal("0"))}, {"label": "Ventas", "value": sum((row.total_amount for row in sales), Decimal("0"))}]}], "filters": [{"name": "date_from", "label": "Fecha desde", "type": "date"}, {"name": "date_to", "label": "Fecha hasta", "type": "date"}, {"name": "status", "label": "Estado", "type": "select", "options": [{"value": key, "label": label} for key, label in PurchaseOrder.STATUS_CHOICES]}]})
    return response({"generated_at": datetime.now().isoformat(), "sections": json_safe(sections)})


def upload_permission(request):
    require_user(request)
    if not request.user.has_perm("DATA_scope.upload_payroll_data"): raise PermissionDenied


@require_http_methods(["GET", "POST"])
def uploads(request):
    upload_permission(request)
    if request.method == "GET":
        rows = [{"id": row.id, "status": row.status, "created_at": row.created_at.isoformat(), "entry_count": row.entry_count, "summary_count": row.summary_count, "error": row.error_message} for row in ImportRun.objects.all()[:20]]
        return response({"uploads": rows, "can_import": request.user.has_perm("DATA_scope.import_payroll_data"), "can_clear": request.user.has_perm("DATA_scope.clear_payroll_data")})
    uploaded = request.FILES.get("file")
    if not uploaded: return response({"error": "Selecciona un archivo CSV, XLSX o XLS."}, 400)
    name = get_valid_filename(uploaded.name)
    if Path(name).suffix.lower() not in {".csv", ".xlsx", ".xls"}: return response({"error": "Formato no soportado."}, 400)
    wants_import = request.POST.get("import") == "true"
    wants_clear = request.POST.get("clear") == "true"
    if wants_import and not request.user.has_perm("DATA_scope.import_payroll_data"): raise PermissionDenied
    if wants_clear and not request.user.has_perm("DATA_scope.clear_payroll_data"): raise PermissionDenied
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    upload_dir = settings.PROJECT_ROOT / "uploads" / run_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    input_path = upload_dir / name
    with input_path.open("wb") as handle:
        for chunk in uploaded.chunks(): handle.write(chunk)
    transformed = upload_dir / "transformed.csv"
    equivalents = upload_dir / "csv_equivalentes_liquidaciones"
    command = [sys.executable, str(settings.PROJECT_ROOT / "run_etl.py"), "--input", str(input_path), "--source-format", request.POST.get("source_format", "auto"), "--transformed-output", str(transformed), "--category-output-dir", str(upload_dir / "csv_por_categoria"), "--equivalent-output-dir", str(equivalents), "--excel-output", str(upload_dir / "Liquidaciones_Historicas_Cargadas.xlsx"), "--rut-empresa", request.POST.get("rut_empresa", "")]
    if request.POST.get("excel") != "true": command.append("--skip-excel")
    if not wants_import: command.append("--skip-import")
    if wants_clear: command.append("--clear")
    config = {"run_id": run_id, "input_name": name, "upload_dir": str(upload_dir), "project_root": str(settings.PROJECT_ROOT), "command": command, "transformed_path": str(transformed), "download_candidates": [["CSV transformado", str(transformed)], ["Resumen generación", str(equivalents / "resumen_generacion.csv")], ["Reporte calidad", str(upload_dir / "reporte_calidad_carga.csv")]], "timeout_seconds": 1800}
    config_path = upload_dir / "job_config.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    (upload_dir / "job_status.json").write_text(json.dumps({"run_id": run_id, "status": "queued", "input_name": name, "return_code": None, "quality_issue_count": 0, "downloads": [], "error": ""}), encoding="utf-8")
    subprocess.Popen([sys.executable, "manage.py", "run_upload_job", str(config_path)], cwd=settings.BASE_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return response({"run_id": run_id, "status": "queued", "input_name": name}, 202)


@require_http_methods(["GET"])
def upload_status(request, run_id):
    upload_permission(request)
    status_path = settings.PROJECT_ROOT / "uploads" / run_id / "job_status.json"
    if not status_path.exists(): return response({"error": "Carga no encontrada."}, 404)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    for item in data.get("downloads", []): item["url"] = f"/cargas/descargar/{run_id}/{item['relative_path']}"
    return response(data)


def security_permission(request):
    require_user(request)
    if not request.user.has_perm("Applet.access_security_module"): raise PermissionDenied


@require_http_methods(["GET", "POST"])
def users(request):
    security_permission(request)
    User = get_user_model(); ensure_role_groups()
    if request.method == "POST":
        data = parse_body(request) or {}
        if not data.get("username") or not data.get("password"): return response({"error": "Usuario y contraseña son obligatorios."}, 400)
        if User.objects.filter(username=data["username"]).exists(): return response({"error": "El usuario ya existe."}, 400)
        user = User.objects.create_user(username=data["username"], password=data["password"], first_name=data.get("first_name", ""), last_name=data.get("last_name", ""), email=data.get("email", ""))
        user.groups.set(Group.objects.filter(name__in=data.get("roles", [])))
        return response({"id": user.id}, 201)
    rows = [{"id": user.id, "username": user.username, "name": user.get_full_name(), "email": user.email, "active": user.is_active, "staff": user.is_staff, "superuser": user.is_superuser, "roles": list(user.groups.values_list("name", flat=True)), "last_login": scalar(user.last_login)} for user in User.objects.prefetch_related("groups").order_by("username")]
    return response({"users": rows, "roles": list(Group.objects.values_list("name", flat=True))})


@require_http_methods(["PATCH"])
def user_detail(request, user_id):
    security_permission(request)
    user = get_object_or_404(get_user_model(), pk=user_id); data = parse_body(request) or {}
    if user == request.user and data.get("active") is False: return response({"error": "No puedes desactivar tu propia cuenta."}, 400)
    for field in ("first_name", "last_name", "email", "is_active", "is_staff"):
        if field in data: setattr(user, field, data[field])
    if data.get("password"): user.set_password(data["password"])
    user.save(); user.groups.set(Group.objects.filter(name__in=data.get("roles", list(user.groups.values_list("name", flat=True)))))
    return response({"ok": True})


@require_http_methods(["GET", "POST"])
def resource_collection(request, resource):
    config = definition(request, resource)
    if config is None:
        return response({"error": "Recurso inexistente."}, 404)
    title, form_class, module = config
    model = form_class.Meta.model
    if request.method == "POST":
        permission = f"{model._meta.app_label}.add_{model._meta.model_name}"
        if not request.user.has_perm(permission):
            raise PermissionDenied
        data = parse_body(request)
        form = form_class(data=data)
        if form.is_valid():
            instance = form.save(commit=False)
            if hasattr(instance, "created_by_id"): instance.created_by = request.user
            if resource == "stock-movements": apply_stock_movement(instance)
            else: instance.save()
            return response({"item": serialize_instance(instance, form_class)}, 201)
        return response({"errors": form.errors.get_json_data()}, 400)

    form = form_class()
    queryset = model.objects.all()
    search = request.GET.get("q", "").strip()
    if search:
        query = models.Q()
        for field in model._meta.fields:
            if isinstance(field, (models.CharField, models.TextField, models.EmailField)):
                query |= models.Q(**{f"{field.name}__icontains": search})
        queryset = queryset.filter(query)
    try: limit = min(max(int(request.GET.get("limit", 100)), 1), 300)
    except ValueError: limit = 100
    rows = [serialize_instance(item, form_class) for item in queryset[:limit]]
    fields = [field_schema(name, field) for name, field in form.fields.items()]
    return response({"key": resource, "title": title, "module": module, "fields": fields, "items": rows, "total": queryset.count(), "can_add": request.user.has_perm(f"{model._meta.app_label}.add_{model._meta.model_name}")})


@require_http_methods(["GET", "PUT", "PATCH"])
def resource_detail(request, resource, object_id):
    config = definition(request, resource)
    if config is None:
        return response({"error": "Recurso inexistente."}, 404)
    _title, form_class, _module = config
    model = form_class.Meta.model
    instance = get_object_or_404(model, pk=object_id)
    if request.method == "GET":
        return response({"item": serialize_instance(instance, form_class)})
    if not request.user.has_perm(f"{model._meta.app_label}.change_{model._meta.model_name}"):
        raise PermissionDenied
    data = parse_body(request)
    form = form_class(data=data, instance=instance)
    if form.is_valid():
        instance = form.save()
        return response({"item": serialize_instance(instance, form_class)})
    return response({"errors": form.errors.get_json_data()}, 400)
