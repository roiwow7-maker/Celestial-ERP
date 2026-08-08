from django.contrib import admin

from .models import AuditLog
from .services import ERP_VERSION


admin.site.site_header = f"Celestial ERP Administracion v{ERP_VERSION}"
admin.site.site_title = f"Celestial ERP v{ERP_VERSION}"
admin.site.index_title = f"Panel Django v{ERP_VERSION}"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "module", "action", "object_type", "object_id", "short_description")
    list_filter = ("module", "action", "object_type", "created_at")
    search_fields = ("user__username", "module", "action", "description", "object_type", "object_id", "object_repr")
    readonly_fields = ("user", "action", "module", "description", "object_type", "object_id", "object_repr", "changes", "created_at")
    date_hierarchy = "created_at"
    list_per_page = 30

    @admin.display(description="Descripcion")
    def short_description(self, obj):
        return obj.description[:90]
