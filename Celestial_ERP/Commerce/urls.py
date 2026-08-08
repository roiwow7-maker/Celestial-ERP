from django.urls import path

from . import views


app_name = "commerce"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("proveedores/", views.suppliers, name="suppliers"),
    path("proveedores/nuevo/", views.supplier_create, name="supplier_create"),
    path("proveedores/<int:supplier_id>/editar/", views.supplier_update, name="supplier_update"),
    path("clientes/", views.customers, name="customers"),
    path("clientes/nuevo/", views.customer_create, name="customer_create"),
    path("clientes/<int:customer_id>/editar/", views.customer_update, name="customer_update"),
    path("compras/", views.purchase_orders, name="purchase_orders"),
    path("compras/nueva/", views.purchase_order_create, name="purchase_order_create"),
    path("compras/<int:order_id>/", views.purchase_order_detail, name="purchase_order_detail"),
    path("compras/<int:order_id>/linea/", views.purchase_line_create, name="purchase_line_create"),
    path("ventas/", views.sales_orders, name="sales_orders"),
    path("ventas/nueva/", views.sales_order_create, name="sales_order_create"),
    path("ventas/<int:order_id>/", views.sales_order_detail, name="sales_order_detail"),
    path("ventas/<int:order_id>/linea/", views.sales_line_create, name="sales_line_create"),
    path("reportes/", views.reports, name="reports"),
]
