from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from Inventory.models import Product


class CommerceTimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Supplier(CommerceTimeStampedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=180)
    tax_id = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=220, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "commerce_supplier"
        ordering = ["name"]
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        permissions = [
            ("access_commerce_module", "Puede acceder al modulo de compras y ventas"),
            ("manage_commerce_partners", "Puede administrar proveedores y clientes"),
            ("manage_purchases", "Puede administrar compras"),
            ("manage_sales", "Puede administrar ventas"),
            ("view_commerce_reports", "Puede ver reportes comerciales"),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Customer(CommerceTimeStampedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=180)
    tax_id = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=220, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "commerce_customer"
        ordering = ["name"]
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class CommercialDocument(CommerceTimeStampedModel):
    STATUS_DRAFT = "draft"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Borrador"),
        (STATUS_CONFIRMED, "Confirmado"),
        (STATUS_CANCELLED, "Anulado"),
    ]

    number = models.CharField(max_length=80, unique=True)
    date = models.DateField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True


class PurchaseOrder(CommercialDocument):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="purchase_orders")
    expected_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "commerce_purchase_order"
        ordering = ["-date", "-id"]
        verbose_name = "Compra"
        verbose_name_plural = "Compras"

    @property
    def total_amount(self) -> Decimal:
        return sum((line.total_amount for line in self.lines.all()), Decimal("0"))

    def __str__(self) -> str:
        return self.number


class PurchaseOrderLine(CommerceTimeStampedModel):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="purchase_lines")
    description = models.CharField(max_length=220, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table = "commerce_purchase_order_line"
        ordering = ["order", "id"]
        verbose_name = "Linea de compra"
        verbose_name_plural = "Lineas de compra"

    @property
    def total_amount(self) -> Decimal:
        return (self.quantity or Decimal("0")) * (self.unit_cost or Decimal("0"))

    def clean(self):
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
        if self.unit_cost is None or self.unit_cost < 0:
            raise ValidationError("El costo unitario no puede ser negativo.")

    def __str__(self) -> str:
        return f"{self.order.number} - {self.product.sku}"


class SalesOrder(CommercialDocument):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="sales_orders")
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "commerce_sales_order"
        ordering = ["-date", "-id"]
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

    @property
    def total_amount(self) -> Decimal:
        return sum((line.total_amount for line in self.lines.all()), Decimal("0"))

    def __str__(self) -> str:
        return self.number


class SalesOrderLine(CommerceTimeStampedModel):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sales_lines")
    description = models.CharField(max_length=220, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table = "commerce_sales_order_line"
        ordering = ["order", "id"]
        verbose_name = "Linea de venta"
        verbose_name_plural = "Lineas de venta"

    @property
    def total_amount(self) -> Decimal:
        return (self.quantity or Decimal("0")) * (self.unit_price or Decimal("0"))

    def clean(self):
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
        if self.unit_price is None or self.unit_price < 0:
            raise ValidationError("El precio unitario no puede ser negativo.")

    def __str__(self) -> str:
        return f"{self.order.number} - {self.product.sku}"
