from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class InventoryTimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Product(InventoryTimeStampedModel):
    UNIT_UNIT = "unidad"
    UNIT_BOX = "caja"
    UNIT_KG = "kg"
    UNIT_LITER = "litro"
    UNIT_SERVICE = "servicio"

    UNIT_CHOICES = [
        (UNIT_UNIT, "Unidad"),
        (UNIT_BOX, "Caja"),
        (UNIT_KG, "Kg"),
        (UNIT_LITER, "Litro"),
        (UNIT_SERVICE, "Servicio"),
    ]

    sku = models.CharField(max_length=48, unique=True)
    name = models.CharField(max_length=180)
    category = models.CharField(max_length=120, blank=True)
    unit = models.CharField(max_length=16, choices=UNIT_CHOICES, default=UNIT_UNIT)
    description = models.TextField(blank=True)
    minimum_stock = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    standard_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "inventory_product"
        ordering = ["sku"]
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        permissions = [
            ("access_inventory_module", "Puede acceder al modulo de inventario"),
            ("manage_inventory_config", "Puede administrar productos y bodegas"),
            ("manage_inventory_stock", "Puede registrar movimientos de inventario"),
            ("view_inventory_reports", "Puede ver reportes de inventario"),
        ]

    def __str__(self) -> str:
        return f"{self.sku} - {self.name}"


class Warehouse(InventoryTimeStampedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=160)
    location = models.CharField(max_length=180, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "inventory_warehouse"
        ordering = ["code"]
        verbose_name = "Bodega"
        verbose_name_plural = "Bodegas"

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class StockBalance(InventoryTimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_balances")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stock_balances")
    quantity = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    average_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "inventory_stock_balance"
        ordering = ["product__sku", "warehouse__code"]
        verbose_name = "Saldo de stock"
        verbose_name_plural = "Saldos de stock"
        constraints = [
            models.UniqueConstraint(fields=["product", "warehouse"], name="inventory_unique_product_warehouse"),
        ]
        indexes = [
            models.Index(fields=["product", "warehouse"]),
            models.Index(fields=["warehouse"]),
        ]

    @property
    def total_value(self) -> Decimal:
        return (self.quantity or Decimal("0")) * (self.average_cost or Decimal("0"))

    @property
    def below_minimum(self) -> bool:
        return self.quantity <= self.product.minimum_stock

    def __str__(self) -> str:
        return f"{self.product.sku} @ {self.warehouse.code}: {self.quantity}"


class StockMovement(InventoryTimeStampedModel):
    TYPE_IN = "in"
    TYPE_OUT = "out"
    TYPE_ADJUSTMENT = "adjustment"

    TYPE_CHOICES = [
        (TYPE_IN, "Entrada"),
        (TYPE_OUT, "Salida"),
        (TYPE_ADJUSTMENT, "Ajuste"),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="stock_movements")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="stock_movements")
    movement_type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    date = models.DateField()
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    reference = models.CharField(max_length=120, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="inventory_movements",
    )
    applied = models.BooleanField(default=False)

    class Meta:
        db_table = "inventory_stock_movement"
        ordering = ["-date", "-id"]
        verbose_name = "Movimiento de stock"
        verbose_name_plural = "Movimientos de stock"
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["movement_type"]),
            models.Index(fields=["product", "warehouse"]),
        ]

    @property
    def signed_quantity(self) -> Decimal:
        if self.movement_type == self.TYPE_OUT:
            return -abs(self.quantity)
        return self.quantity

    @property
    def total_cost(self) -> Decimal:
        return abs(self.quantity or Decimal("0")) * (self.unit_cost or Decimal("0"))

    def clean(self):
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
        if self.unit_cost is not None and self.unit_cost < 0:
            raise ValidationError("El costo unitario no puede ser negativo.")

    def __str__(self) -> str:
        return f"{self.get_movement_type_display()} {self.product.sku} {self.quantity}"
