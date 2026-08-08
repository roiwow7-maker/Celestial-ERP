from django.contrib import admin

from .models import ChartAccount, CostCenter, JournalEntry, JournalEntryLine, PayrollItemAccountMapping


@admin.register(ChartAccount)
class ChartAccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "account_type", "parent", "is_active")
    list_filter = ("account_type", "is_active")
    search_fields = ("code", "name")
    list_per_page = 30


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "description")
    list_per_page = 30


@admin.register(PayrollItemAccountMapping)
class PayrollItemAccountMappingAdmin(admin.ModelAdmin):
    list_display = ("payroll_item", "account", "movement_type", "cost_center", "is_active")
    list_filter = ("movement_type", "is_active", "account__account_type", "payroll_item__categoria")
    search_fields = ("payroll_item__codigo", "payroll_item__descripcion", "account__code", "account__name")
    autocomplete_fields = ("payroll_item", "account", "cost_center")
    list_select_related = ("payroll_item", "account", "cost_center")
    list_per_page = 30


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 0
    autocomplete_fields = ("account", "cost_center")


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("number", "period", "date", "status", "source", "total_debit", "total_credit", "is_balanced")
    list_filter = ("status", "source", "period")
    search_fields = ("number", "description")
    autocomplete_fields = ("period",)
    inlines = [JournalEntryLineInline]
    list_per_page = 30


@admin.register(JournalEntryLine)
class JournalEntryLineAdmin(admin.ModelAdmin):
    list_display = ("journal_entry", "account", "cost_center", "debit", "credit")
    list_filter = ("account__account_type", "cost_center")
    search_fields = ("journal_entry__number", "account__code", "account__name", "description")
    autocomplete_fields = ("journal_entry", "account", "cost_center")
    list_select_related = ("journal_entry", "account", "cost_center")
    list_per_page = 30
