from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import DecimalField, ExpressionWrapper, F, Sum

from .models import Product, StockBalance, StockMovement, Warehouse


@transaction.atomic
def apply_stock_movement(movement: StockMovement) -> StockMovement:
    if movement.applied:
        return movement

    movement.full_clean()
    if movement.pk is None:
        movement.save()
    balance, _ = StockBalance.objects.select_for_update().get_or_create(
        product=movement.product,
        warehouse=movement.warehouse,
        defaults={"quantity": Decimal("0"), "average_cost": movement.product.standard_cost},
    )

    current_quantity = balance.quantity or Decimal("0")
    current_cost = balance.average_cost or Decimal("0")
    quantity = movement.quantity or Decimal("0")

    if movement.movement_type == StockMovement.TYPE_IN:
        new_quantity = current_quantity + quantity
        if new_quantity > 0:
            current_value = current_quantity * current_cost
            incoming_value = quantity * (movement.unit_cost or Decimal("0"))
            balance.average_cost = (current_value + incoming_value) / new_quantity
        balance.quantity = new_quantity
    elif movement.movement_type == StockMovement.TYPE_OUT:
        if current_quantity < quantity:
            raise ValidationError("No hay stock suficiente para registrar la salida.")
        balance.quantity = current_quantity - quantity
    else:
        balance.quantity = quantity
        balance.average_cost = movement.unit_cost or current_cost

    balance.save()
    movement.applied = True
    movement.save(update_fields=["applied", "updated_at"])
    return movement


def inventory_summary() -> dict[str, object]:
    stock_value_expression = ExpressionWrapper(
        F("quantity") * F("average_cost"),
        output_field=DecimalField(max_digits=20, decimal_places=2),
    )
    totals = StockBalance.objects.aggregate(
        total_quantity=Sum("quantity"),
        total_value=Sum(stock_value_expression),
    )
    return {
        "products": Product.objects.count(),
        "active_products": Product.objects.filter(is_active=True).count(),
        "warehouses": Warehouse.objects.count(),
        "movements": StockMovement.objects.count(),
        "stock_quantity": totals["total_quantity"] or Decimal("0"),
        "stock_value": totals["total_value"] or Decimal("0"),
        "low_stock": StockBalance.objects.filter(quantity__lte=F("product__minimum_stock")).count(),
        "categories": Product.objects.exclude(category="").values("category").distinct().count(),
    }


def valuation_rows():
    return (
        StockBalance.objects.select_related("product", "warehouse")
        .annotate(total_value=F("quantity") * F("average_cost"))
        .order_by("product__sku", "warehouse__code")
    )


def category_valuation_rows():
    grouped = {}
    for balance in StockBalance.objects.select_related("product"):
        category = balance.product.category or ""
        row = grouped.setdefault(
            category,
            {"product__category": category, "product_ids": set(), "quantity": Decimal("0"), "value": Decimal("0")},
        )
        row["product_ids"].add(balance.product_id)
        row["quantity"] += balance.quantity or Decimal("0")
        row["value"] += balance.total_value

    rows = []
    for row in grouped.values():
        row["products"] = len(row.pop("product_ids"))
        rows.append(row)
    return sorted(rows, key=lambda item: item["product__category"])
