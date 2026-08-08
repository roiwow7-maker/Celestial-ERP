from django.contrib import admin

from Applet.services import ERP_VERSION

from .models import Employee, ImportRun, PayrollEntry, PayrollItem, PayrollPeriod, PayrollSummary


admin.site.site_header = f"Celestial ERP Administracion v{ERP_VERSION}"
admin.site.site_title = f"Celestial ERP v{ERP_VERSION}"
admin.site.index_title = f"Panel Django v{ERP_VERSION}"
admin.site.empty_value_display = "Sin dato"


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("codigo_ficha", "rut", "nombre", "estado", "division", "afp", "isapre", "fecha_ingreso")
    search_fields = ("codigo_ficha", "rut", "nombre")
    list_filter = ("estado", "division", "afp", "isapre")
    list_per_page = 30
    search_help_text = "Busca por codigo de ficha, RUT o nombre del trabajador."
    fieldsets = (
        ("Identificacion", {"fields": ("codigo_ficha", "rut", "nombre", "estado", "division")}),
        ("Prevision y salud", {"fields": ("afp", "isapre")}),
        ("Datos laborales", {"fields": ("fecha_ingreso", "fecha_retiro", "horario_trabajo", "jornada_vs", "jornada_contrato")}),
    )


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ("periodo", "year", "month")
    search_fields = ("periodo",)
    list_filter = ("year", "month")
    list_per_page = 30
    search_help_text = "Busca por periodo en formato AAAAMM, por ejemplo 202606."


@admin.register(PayrollItem)
class PayrollItemAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descripcion", "categoria", "requiere_confirmacion")
    search_fields = ("codigo", "descripcion")
    list_filter = ("categoria", "requiere_confirmacion")
    list_per_page = 30
    search_help_text = "Busca por codigo o descripcion del item de remuneracion."
    fieldsets = (
        ("Concepto", {"fields": ("codigo", "descripcion")}),
        ("Clasificacion", {"fields": ("categoria", "requiere_confirmacion")}),
    )


@admin.register(PayrollEntry)
class PayrollEntryAdmin(admin.ModelAdmin):
    list_display = ("period", "employee_code", "employee_name", "item_code", "item_category", "monto")
    search_fields = (
        "employee__codigo_ficha",
        "employee__rut",
        "employee__nombre",
        "item__codigo",
        "item__descripcion",
    )
    list_filter = ("period", "item__categoria")
    list_select_related = ("employee", "period", "item")
    autocomplete_fields = ("employee", "period", "item")
    list_per_page = 30
    show_full_result_count = False
    search_help_text = "Busca por trabajador, RUT, codigo de ficha, codigo de item o descripcion."

    @admin.display(description="Ficha", ordering="employee__codigo_ficha")
    def employee_code(self, obj):
        return obj.employee.codigo_ficha

    @admin.display(description="Trabajador", ordering="employee__nombre")
    def employee_name(self, obj):
        return obj.employee.nombre

    @admin.display(description="Item", ordering="item__codigo")
    def item_code(self, obj):
        return obj.item.codigo

    @admin.display(description="Categoria", ordering="item__categoria")
    def item_category(self, obj):
        return obj.item.categoria


@admin.register(PayrollSummary)
class PayrollSummaryAdmin(admin.ModelAdmin):
    list_display = (
        "document_number",
        "employee_code",
        "employee_name",
        "period",
        "sueldo_liquido",
        "costo_empresa",
        "total_haberes_imponibles",
        "total_descuentos_legales",
        "total_otros_descuentos",
    )
    search_fields = ("document_number", "employee__codigo_ficha", "employee__rut", "employee__nombre")
    list_filter = ("period",)
    list_select_related = ("employee", "period")
    autocomplete_fields = ("employee", "period")
    list_per_page = 30
    show_full_result_count = False
    search_help_text = "Busca por numero de documento, codigo de ficha, RUT o nombre."
    fieldsets = (
        ("Identificacion", {"fields": ("document_number", "employee", "period", "rut_empresa")}),
        ("Dias y jornada", {"fields": ("dias_laborales", "dias_trabajados", "dias_licencias", "dias_permisos", "dias_ausencias", "dias_suspendidos", "horas_no_trabajadas", "horas_extras")}),
        ("Totales principales", {"fields": ("sueldo_base", "costo_empresa", "total_haberes_imponibles", "total_haberes_no_imponibles", "total_descuentos_legales", "total_otros_descuentos", "sueldo_liquido")}),
        ("Prevision, salud e impuestos", {"fields": ("base_tributable", "impuesto", "pago_prevision", "pago_salud_obligatoria", "pago_salud_voluntaria", "pago_prevision_voluntaria", "seguro_cesantia_trabajador")}),
        ("Aportes empleador", {"fields": ("seguro_cesantia_empleador", "mutual_empleador", "pago_sis_empleador", "afp_prevision_empleador", "ley_sanna", "otros_aportes_patronales", "saldo_sobregiro")}),
    )

    @admin.display(description="Ficha", ordering="employee__codigo_ficha")
    def employee_code(self, obj):
        return obj.employee.codigo_ficha

    @admin.display(description="Trabajador", ordering="employee__nombre")
    def employee_name(self, obj):
        return obj.employee.nombre


@admin.register(ImportRun)
class ImportRunAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "status",
        "clear_requested",
        "employee_count",
        "period_count",
        "item_count",
        "entry_count",
        "summary_count",
    )
    list_filter = ("status", "clear_requested")
    search_fields = ("transformed_path", "summaries_path", "transformed_sha256", "summaries_sha256")
    list_per_page = 20
    date_hierarchy = "created_at"
    search_help_text = "Busca por ruta de archivo o hash de control."
    readonly_fields = (
        "created_at",
        "updated_at",
        "transformed_sha256",
        "summaries_sha256",
        "transformed_path",
        "summaries_path",
        "descriptions_dir",
        "employee_count",
        "period_count",
        "item_count",
        "entry_count",
        "summary_count",
        "error_message",
    )
    fieldsets = (
        ("Estado de la carga", {"fields": ("status", "clear_requested", "created_at", "updated_at", "error_message")}),
        ("Archivos procesados", {"fields": ("transformed_path", "summaries_path", "descriptions_dir", "transformed_sha256", "summaries_sha256")}),
        ("Conteos importados", {"fields": ("employee_count", "period_count", "item_count", "entry_count", "summary_count")}),
    )
