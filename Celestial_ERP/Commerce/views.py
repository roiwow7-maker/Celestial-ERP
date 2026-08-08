from __future__ import annotations

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from Applet.access import module_permission_required

from .forms import CustomerForm, PurchaseOrderForm, PurchaseOrderLineForm, SalesOrderForm, SalesOrderLineForm, SupplierForm
from .models import Customer, PurchaseOrder, SalesOrder, Supplier
from .services import commerce_summary, partner_activity_rows


@module_permission_required("Commerce.access_commerce_module")
def dashboard(request):
    return render(
        request,
        "Commerce/dashboard.html",
        {
            "summary": commerce_summary(),
            "recent_purchases": PurchaseOrder.objects.select_related("supplier").prefetch_related("lines")[:6],
            "recent_sales": SalesOrder.objects.select_related("customer").prefetch_related("lines")[:6],
        },
    )


@module_permission_required("Commerce.access_commerce_module")
def suppliers(request):
    query = request.GET.get("q", "").strip()
    rows = Supplier.objects.all()
    if query:
        rows = rows.filter(Q(code__icontains=query) | Q(name__icontains=query) | Q(tax_id__icontains=query))
    return render(request, "Commerce/suppliers.html", {"suppliers": rows, "query": query})


@module_permission_required("Commerce.manage_commerce_partners")
def supplier_create(request):
    return commerce_form_view(request, SupplierForm, "Nuevo proveedor", "commerce:suppliers")


@module_permission_required("Commerce.manage_commerce_partners")
def supplier_update(request, supplier_id: int):
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    return commerce_form_view(request, SupplierForm, "Editar proveedor", "commerce:suppliers", instance=supplier)


@module_permission_required("Commerce.access_commerce_module")
def customers(request):
    query = request.GET.get("q", "").strip()
    rows = Customer.objects.all()
    if query:
        rows = rows.filter(Q(code__icontains=query) | Q(name__icontains=query) | Q(tax_id__icontains=query))
    return render(request, "Commerce/customers.html", {"customers": rows, "query": query})


@module_permission_required("Commerce.manage_commerce_partners")
def customer_create(request):
    return commerce_form_view(request, CustomerForm, "Nuevo cliente", "commerce:customers")


@module_permission_required("Commerce.manage_commerce_partners")
def customer_update(request, customer_id: int):
    customer = get_object_or_404(Customer, pk=customer_id)
    return commerce_form_view(request, CustomerForm, "Editar cliente", "commerce:customers", instance=customer)


@module_permission_required("Commerce.access_commerce_module")
def purchase_orders(request):
    orders = PurchaseOrder.objects.select_related("supplier").prefetch_related("lines")
    return render(request, "Commerce/purchase_orders.html", {"orders": orders})


@module_permission_required("Commerce.manage_purchases")
def purchase_order_create(request):
    return document_form_view(request, PurchaseOrderForm, "Nueva compra", "commerce:purchase_orders")


@module_permission_required("Commerce.access_commerce_module")
def purchase_order_detail(request, order_id: int):
    order = get_object_or_404(PurchaseOrder.objects.select_related("supplier").prefetch_related("lines__product"), pk=order_id)
    return render(request, "Commerce/purchase_detail.html", {"order": order})


@module_permission_required("Commerce.manage_purchases")
def purchase_line_create(request, order_id: int):
    order = get_object_or_404(PurchaseOrder, pk=order_id)
    form = PurchaseOrderLineForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        line = form.save(commit=False)
        line.order = order
        line.save()
        messages.success(request, "Linea de compra agregada.")
        return redirect("commerce:purchase_order_detail", order_id=order.id)
    return render(request, "Commerce/model_form.html", {"form": form, "title": "Nueva linea de compra", "back_url": "commerce:purchase_order_detail", "back_arg": order.id})


@module_permission_required("Commerce.access_commerce_module")
def sales_orders(request):
    orders = SalesOrder.objects.select_related("customer").prefetch_related("lines")
    return render(request, "Commerce/sales_orders.html", {"orders": orders})


@module_permission_required("Commerce.manage_sales")
def sales_order_create(request):
    return document_form_view(request, SalesOrderForm, "Nueva venta", "commerce:sales_orders")


@module_permission_required("Commerce.access_commerce_module")
def sales_order_detail(request, order_id: int):
    order = get_object_or_404(SalesOrder.objects.select_related("customer").prefetch_related("lines__product"), pk=order_id)
    return render(request, "Commerce/sales_detail.html", {"order": order})


@module_permission_required("Commerce.manage_sales")
def sales_line_create(request, order_id: int):
    order = get_object_or_404(SalesOrder, pk=order_id)
    form = SalesOrderLineForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        line = form.save(commit=False)
        line.order = order
        line.save()
        messages.success(request, "Linea de venta agregada.")
        return redirect("commerce:sales_order_detail", order_id=order.id)
    return render(request, "Commerce/model_form.html", {"form": form, "title": "Nueva linea de venta", "back_url": "commerce:sales_order_detail", "back_arg": order.id})


@module_permission_required("Commerce.view_commerce_reports")
def reports(request):
    supplier_rows, customer_rows = partner_activity_rows()
    return render(request, "Commerce/reports.html", {"summary": commerce_summary(), "suppliers": supplier_rows, "customers": customer_rows})


def commerce_form_view(request, form_class, title: str, back_url: str, instance=None):
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Registro guardado.")
        return redirect(back_url)
    return render(request, "Commerce/model_form.html", {"form": form, "title": title, "back_url": back_url})


def document_form_view(request, form_class, title: str, back_url: str):
    initial = {"date": timezone.localdate()}
    form = form_class(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        document = form.save(commit=False)
        document.created_by = request.user if request.user.is_authenticated else None
        document.save()
        messages.success(request, "Documento guardado.")
        return redirect(back_url)
    return render(request, "Commerce/model_form.html", {"form": form, "title": title, "back_url": back_url})
