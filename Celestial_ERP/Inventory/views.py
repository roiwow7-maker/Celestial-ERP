from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from Applet.access import module_permission_required

from .forms import ProductForm, StockMovementForm, WarehouseForm
from .models import Product, StockBalance, StockMovement, Warehouse
from .services import apply_stock_movement, category_valuation_rows, inventory_summary, valuation_rows


@module_permission_required("Inventory.access_inventory_module")
def dashboard(request):
    recent_movements = StockMovement.objects.select_related("product", "warehouse").order_by("-created_at")[:8]
    return render(
        request,
        "Inventory/dashboard.html",
        {
            "summary": inventory_summary(),
            "recent_movements": recent_movements,
        },
    )


@module_permission_required("Inventory.access_inventory_module")
def products(request):
    query = request.GET.get("q", "").strip()
    products_qs = Product.objects.all()
    if query:
        products_qs = products_qs.filter(Q(sku__icontains=query) | Q(name__icontains=query) | Q(category__icontains=query))
    return render(request, "Inventory/products.html", {"products": products_qs, "query": query})


@module_permission_required("Inventory.manage_inventory_config")
def product_create(request):
    return inventory_form_view(request, ProductForm, "Nuevo producto", "inventory:products")


@module_permission_required("Inventory.manage_inventory_config")
def product_update(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id)
    return inventory_form_view(request, ProductForm, "Editar producto", "inventory:products", instance=product)


@module_permission_required("Inventory.access_inventory_module")
def warehouses(request):
    query = request.GET.get("q", "").strip()
    warehouses_qs = Warehouse.objects.all()
    if query:
        warehouses_qs = warehouses_qs.filter(Q(code__icontains=query) | Q(name__icontains=query) | Q(location__icontains=query))
    return render(request, "Inventory/warehouses.html", {"warehouses": warehouses_qs, "query": query})


@module_permission_required("Inventory.manage_inventory_config")
def warehouse_create(request):
    return inventory_form_view(request, WarehouseForm, "Nueva bodega", "inventory:warehouses")


@module_permission_required("Inventory.manage_inventory_config")
def warehouse_update(request, warehouse_id: int):
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
    return inventory_form_view(request, WarehouseForm, "Editar bodega", "inventory:warehouses", instance=warehouse)


@module_permission_required("Inventory.access_inventory_module")
def stock(request):
    balances = StockBalance.objects.select_related("product", "warehouse").order_by("product__sku", "warehouse__code")
    return render(request, "Inventory/stock.html", {"balances": balances})


@module_permission_required("Inventory.access_inventory_module")
def movements(request):
    movements_qs = StockMovement.objects.select_related("product", "warehouse", "created_by").order_by("-date", "-id")
    return render(request, "Inventory/movements.html", {"movements": movements_qs})


@module_permission_required("Inventory.manage_inventory_stock")
def movement_create(request):
    initial = {"date": timezone.localdate()}
    form = StockMovementForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        movement = form.save(commit=False)
        movement.created_by = request.user if request.user.is_authenticated else None
        try:
            apply_stock_movement(movement)
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Movimiento registrado y stock actualizado.")
            return redirect("inventory:movements")
    return render(request, "Inventory/model_form.html", {"form": form, "title": "Nuevo movimiento", "back_url": "inventory:movements"})


@module_permission_required("Inventory.view_inventory_reports")
def valuation(request):
    return render(
        request,
        "Inventory/valuation.html",
        {
            "summary": inventory_summary(),
            "balances": valuation_rows(),
            "categories": category_valuation_rows(),
        },
    )


def inventory_form_view(request, form_class, title: str, back_url: str, instance=None):
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Registro guardado.")
        return redirect(back_url)
    return render(request, "Inventory/model_form.html", {"form": form, "title": title, "back_url": back_url})
