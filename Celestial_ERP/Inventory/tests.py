from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Product, StockBalance, StockMovement, Warehouse
from .services import apply_stock_movement, inventory_summary


class InventoryStockTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(sku="GUANTE-01", name="Guante operativo", minimum_stock=Decimal("5"))
        self.warehouse = Warehouse.objects.create(code="GEN", name="Bodega general")

    def test_entry_updates_stock_and_average_cost(self):
        movement = StockMovement.objects.create(
            product=self.product,
            warehouse=self.warehouse,
            movement_type=StockMovement.TYPE_IN,
            date=date(2026, 7, 13),
            quantity=Decimal("10"),
            unit_cost=Decimal("2500"),
        )

        apply_stock_movement(movement)

        balance = StockBalance.objects.get(product=self.product, warehouse=self.warehouse)
        self.assertEqual(balance.quantity, Decimal("10.00"))
        self.assertEqual(balance.average_cost, Decimal("2500.00"))
        self.assertTrue(StockMovement.objects.get(pk=movement.pk).applied)

    def test_outgoing_movement_reduces_stock(self):
        apply_stock_movement(
            StockMovement.objects.create(
                product=self.product,
                warehouse=self.warehouse,
                movement_type=StockMovement.TYPE_IN,
                date=date(2026, 7, 13),
                quantity=Decimal("10"),
                unit_cost=Decimal("2500"),
            )
        )
        apply_stock_movement(
            StockMovement.objects.create(
                product=self.product,
                warehouse=self.warehouse,
                movement_type=StockMovement.TYPE_OUT,
                date=date(2026, 7, 13),
                quantity=Decimal("3"),
                unit_cost=Decimal("0"),
            )
        )

        balance = StockBalance.objects.get(product=self.product, warehouse=self.warehouse)
        self.assertEqual(balance.quantity, Decimal("7.00"))
        self.assertEqual(inventory_summary()["stock_value"], Decimal("17500"))

    def test_insufficient_stock_does_not_store_unapplied_movement(self):
        movement = StockMovement(
            product=self.product,
            warehouse=self.warehouse,
            movement_type=StockMovement.TYPE_OUT,
            date=date(2026, 7, 13),
            quantity=Decimal("3"),
            unit_cost=Decimal("0"),
        )

        with self.assertRaises(ValidationError):
            apply_stock_movement(movement)

        self.assertEqual(StockMovement.objects.count(), 0)
        self.assertEqual(StockBalance.objects.count(), 0)


class InventoryRouteTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="inventario", password="test12345")
        permission = Permission.objects.get(codename="access_inventory_module", content_type__app_label="Inventory")
        report_permission = Permission.objects.get(codename="view_inventory_reports", content_type__app_label="Inventory")
        self.user.user_permissions.add(permission, report_permission)

    def test_dashboard_requires_inventory_permission(self):
        self.client.login(username="inventario", password="test12345")
        response = self.client.get(reverse("inventory:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inventario")

    def test_valuation_requires_report_permission(self):
        self.client.login(username="inventario", password="test12345")
        response = self.client.get(reverse("inventory:valuation"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Valorizacion")
