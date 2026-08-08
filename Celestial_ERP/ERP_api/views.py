import json

from django.contrib.auth.decorators import login_required, permission_required
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET

from Applet.services import ERP_VERSION, auto_backup_enabled, auto_backup_interval_minutes, latest_backup_file
from DATA_scope.models import Employee, ImportRun, PayrollEntry, PayrollItem, PayrollPeriod, PayrollSummary


def json_response(data, status=200):
    return JsonResponse(data, status=status, json_dumps_params={"ensure_ascii": False})


def wants_json(request) -> bool:
    return request.GET.get("format") == "json" or "application/json" in request.headers.get("Accept", "")


def endpoint_url(request, route_name: str) -> str:
    return request.build_absolute_uri(reverse(route_name))


def endpoint_catalog(request):
    can_payroll = request.user.has_perm("DATA_scope.access_payroll_module")
    endpoints = [
        {
            "key": "health",
            "title": "Salud",
            "method": "GET",
            "url": endpoint_url(request, "erp_api:health"),
            "path": reverse("erp_api:health"),
            "permission": "Login",
            "description": "Confirma que el servicio Celestial ERP esta operativo.",
            "available": True,
            "sample": health_data(),
        },
        {
            "key": "system_status",
            "title": "Estado del sistema",
            "method": "GET",
            "url": endpoint_url(request, "erp_api:system_status"),
            "path": reverse("erp_api:system_status"),
            "permission": "Login",
            "description": "Estado general de Django, base de datos, ultima carga, backups y version.",
            "available": True,
            "sample": system_status_data(),
        },
        {
            "key": "modules",
            "title": "Modulos",
            "method": "GET",
            "url": endpoint_url(request, "erp_api:modules"),
            "path": reverse("erp_api:modules"),
            "permission": "DATA_scope.access_payroll_module",
            "description": "Lista de modulos activos y rutas web principales.",
            "available": can_payroll,
            "sample": modules_data() if can_payroll else {"error": "Requiere permiso DATA_scope.access_payroll_module"},
        },
        {
            "key": "payroll_summary",
            "title": "Resumen remuneraciones",
            "method": "GET",
            "url": endpoint_url(request, "erp_api:payroll_summary"),
            "path": reverse("erp_api:payroll_summary"),
            "permission": "DATA_scope.access_payroll_module",
            "description": "Conteos generales de trabajadores, periodos, items, movimientos y liquidaciones.",
            "available": can_payroll,
            "sample": payroll_summary_data() if can_payroll else {"error": "Requiere permiso DATA_scope.access_payroll_module"},
        },
        {
            "key": "payroll_periods",
            "title": "Periodos recientes",
            "method": "GET",
            "url": endpoint_url(request, "erp_api:payroll_periods"),
            "path": reverse("erp_api:payroll_periods"),
            "permission": "DATA_scope.access_payroll_module",
            "description": "Ultimos 24 periodos disponibles para remuneraciones.",
            "available": can_payroll,
            "sample": payroll_periods_data(limit=5) if can_payroll else {"error": "Requiere permiso DATA_scope.access_payroll_module"},
        },
    ]
    for endpoint in endpoints:
        endpoint["sample_json"] = json.dumps(endpoint["sample"], ensure_ascii=False, indent=2, default=str)
    return endpoints


@require_GET
@login_required
def index(request):
    endpoints = endpoint_catalog(request)
    if wants_json(request):
        return json_response(
            {
                "name": "Celestial ERP API",
                "version": ERP_VERSION,
                "endpoints": {
                    endpoint["key"]: endpoint["url"]
                    for endpoint in endpoints
                },
            }
        )
    return render(
        request,
        "ERP_api/index.html",
        {
            "name": "Celestial ERP API",
            "version": ERP_VERSION,
            "endpoints": endpoints,
        },
    )


@require_GET
@login_required
def health(request):
    return json_response(health_data())


@require_GET
@login_required
def system_status(request):
    return json_response(system_status_data())


@require_GET
@permission_required("DATA_scope.access_payroll_module", raise_exception=True)
def modules(request):
    return json_response(modules_data())


@require_GET
@permission_required("DATA_scope.access_payroll_module", raise_exception=True)
def payroll_summary(request):
    return json_response(payroll_summary_data())


@require_GET
@permission_required("DATA_scope.access_payroll_module", raise_exception=True)
def payroll_periods(request):
    return json_response(payroll_periods_data())


def health_data():
    return {"status": "ok", "service": "Celestial ERP", "version": ERP_VERSION}


def system_status_data():
    database_status = "connected"
    try:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            cursor.fetchone()
    except Exception:
        database_status = "error"

    latest_import = ImportRun.objects.order_by("-created_at").first()
    latest_backup = latest_backup_file()
    return {
        "django": "operativo",
        "database": database_status,
        "data_scope": "activo",
        "external_etl": "disponible",
        "latest_import": serialize_import_run(latest_import),
        "latest_backup": latest_backup,
        "auto_backup": {
            "enabled": auto_backup_enabled(),
            "interval_minutes": auto_backup_interval_minutes(),
        },
        "version": ERP_VERSION,
    }


def modules_data():
    return {
        "modules": [
            {"code": "payroll", "name": "RRHH / Remuneraciones", "status": "active", "url": reverse("data_scope:payroll_dashboard")},
            {"code": "reports", "name": "Reportes", "status": "active", "url": reverse("data_scope:reports")},
            {"code": "etl_uploads", "name": "Cargas ETL", "status": "active", "url": reverse("data_scope:upload_data")},
            {"code": "attendance", "name": "Asistencia", "status": "active", "url": reverse("attendance:dashboard")},
            {"code": "accounting", "name": "Contabilidad", "status": "active", "url": reverse("accounting:dashboard")},
            {"code": "inventory", "name": "Inventario", "status": "active", "url": reverse("inventory:dashboard")},
            {"code": "commerce", "name": "Compras y ventas", "status": "active", "url": reverse("commerce:dashboard")},
            {"code": "settings", "name": "Configuracion", "status": "base", "url": reverse("applet:admin_panel")},
        ]
    }


def payroll_summary_data():
    latest_import = ImportRun.objects.order_by("-created_at").first()
    return {
        "employees": Employee.objects.count(),
        "periods": PayrollPeriod.objects.count(),
        "items": PayrollItem.objects.count(),
        "entries": PayrollEntry.objects.count(),
        "summaries": PayrollSummary.objects.count(),
        "latest_import": serialize_import_run(latest_import),
    }


def payroll_periods_data(limit=24):
    periods = PayrollPeriod.objects.order_by("-periodo")[:limit]
    return {
        "periods": [
            {"periodo": period.periodo, "year": period.year, "month": period.month}
            for period in periods
        ]
    }


def serialize_import_run(import_run):
    if import_run is None:
        return None
    return {
        "id": import_run.id,
        "status": import_run.status,
        "created_at": import_run.created_at.isoformat(),
        "entry_count": import_run.entry_count,
        "summary_count": import_run.summary_count,
        "clear_requested": import_run.clear_requested,
    }
