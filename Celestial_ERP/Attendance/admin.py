from django.contrib import admin

from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("date", "employee", "check_in", "check_out", "break_minutes", "worked_hours", "status", "source")
    list_filter = ("status", "source", "date")
    search_fields = ("employee__codigo_ficha", "employee__nombre", "employee__rut", "notes")
    autocomplete_fields = ("employee", "created_by")
    list_select_related = ("employee", "created_by")
    date_hierarchy = "date"
    list_per_page = 40
