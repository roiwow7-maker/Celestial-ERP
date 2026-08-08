from django.contrib import admin

from .models import Product, StockBalance, StockMovement, Warehouse


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "unit", "minimum_stock", "standard_cost", "is_active")
    list_filter = ("is_active", "unit", "category")
    search_fields = ("sku", "name", "category", "description")
    list_per_page = 30


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "location", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "location")
    list_per_page = 30


@admin.register(StockBalance)
class StockBalanceAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "quantity", "average_cost", "total_value", "below_minimum")
    list_filter = ("warehouse", "product__category")
    search_fields = ("product__sku", "product__name", "warehouse__code", "warehouse__name")
    autocomplete_fields = ("product", "warehouse")
    list_select_related = ("product", "warehouse")
    list_per_page = 30


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("date", "movement_type", "product", "warehouse", "quantity", "unit_cost", "applied", "created_by")
    list_filter = ("movement_type", "applied", "warehouse")
    search_fields = ("product__sku", "product__name", "reference", "note")
    autocomplete_fields = ("product", "warehouse", "created_by")
    list_select_related = ("product", "warehouse", "created_by")
    list_per_page = 30
