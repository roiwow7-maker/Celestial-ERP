from django.urls import path

from . import views


app_name = "inventory"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("productos/", views.products, name="products"),
    path("productos/nuevo/", views.product_create, name="product_create"),
    path("productos/<int:product_id>/editar/", views.product_update, name="product_update"),
    path("bodegas/", views.warehouses, name="warehouses"),
    path("bodegas/nueva/", views.warehouse_create, name="warehouse_create"),
    path("bodegas/<int:warehouse_id>/editar/", views.warehouse_update, name="warehouse_update"),
    path("stock/", views.stock, name="stock"),
    path("movimientos/", views.movements, name="movements"),
    path("movimientos/nuevo/", views.movement_create, name="movement_create"),
    path("valorizacion/", views.valuation, name="valuation"),
]
