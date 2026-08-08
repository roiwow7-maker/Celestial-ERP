from django.contrib import admin

from .models import Customer, PurchaseOrder, PurchaseOrderLine, SalesOrder, SalesOrderLine, Supplier


class PurchaseOrderLineInline(admin.TabularInline):
    model = PurchaseOrderLine
    extra = 0
    autocomplete_fields = ("product",)


class SalesOrderLineInline(admin.TabularInline):
    model = SalesOrderLine
    extra = 0
    autocomplete_fields = ("product",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "tax_id", "email", "phone", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "tax_id", "email")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "tax_id", "email", "phone", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "tax_id", "email")


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "supplier", "date", "expected_date", "status", "total_amount")
    list_filter = ("status", "date")
    search_fields = ("number", "supplier__name", "supplier__code")
    autocomplete_fields = ("supplier", "created_by")
    inlines = [PurchaseOrderLineInline]


@admin.register(PurchaseOrderLine)
class PurchaseOrderLineAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "unit_cost", "total_amount")
    search_fields = ("order__number", "product__sku", "product__name", "description")
    autocomplete_fields = ("order", "product")


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "customer", "date", "due_date", "status", "total_amount")
    list_filter = ("status", "date")
    search_fields = ("number", "customer__name", "customer__code")
    autocomplete_fields = ("customer", "created_by")
    inlines = [SalesOrderLineInline]


@admin.register(SalesOrderLine)
class SalesOrderLineAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "unit_price", "total_amount")
    search_fields = ("order__number", "product__sku", "product__name", "description")
    autocomplete_fields = ("order", "product")
