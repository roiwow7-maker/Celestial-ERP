from __future__ import annotations

from decimal import Decimal

from django.db.models import Count

from .models import Customer, PurchaseOrder, PurchaseOrderLine, SalesOrder, SalesOrderLine, Supplier


def commerce_summary() -> dict[str, object]:
    purchase_total = sum((order.total_amount for order in PurchaseOrder.objects.prefetch_related("lines")), Decimal("0"))
    sales_total = sum((order.total_amount for order in SalesOrder.objects.prefetch_related("lines")), Decimal("0"))
    return {
        "suppliers": Supplier.objects.count(),
        "customers": Customer.objects.count(),
        "purchase_orders": PurchaseOrder.objects.count(),
        "sales_orders": SalesOrder.objects.count(),
        "purchase_lines": PurchaseOrderLine.objects.count(),
        "sales_lines": SalesOrderLine.objects.count(),
        "purchase_total": purchase_total,
        "sales_total": sales_total,
        "open_purchases": PurchaseOrder.objects.exclude(status=PurchaseOrder.STATUS_CANCELLED).count(),
        "open_sales": SalesOrder.objects.exclude(status=SalesOrder.STATUS_CANCELLED).count(),
    }


def partner_activity_rows():
    suppliers = Supplier.objects.annotate(document_count=Count("purchase_orders")).order_by("name")
    customers = Customer.objects.annotate(document_count=Count("sales_orders")).order_by("name")
    return suppliers, customers
