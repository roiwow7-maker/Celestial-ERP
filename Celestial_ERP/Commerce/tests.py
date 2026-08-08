from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from Inventory.models import Product

from .models import Customer, PurchaseOrder, PurchaseOrderLine, SalesOrder, SalesOrderLine, Supplier
from .services import commerce_summary


class CommerceDocumentTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(sku="SERV-01", name="Servicio operativo", standard_cost=Decimal("1000"))
        self.supplier = Supplier.objects.create(code="PROV-01", name="Proveedor base")
        self.customer = Customer.objects.create(code="CLI-01", name="Cliente base")

    def test_purchase_order_total(self):
        order = PurchaseOrder.objects.create(number="OC-001", supplier=self.supplier, date=date(2026, 7, 13))
        PurchaseOrderLine.objects.create(order=order, product=self.product, quantity=Decimal("2"), unit_cost=Decimal("1500"))

        self.assertEqual(order.total_amount, Decimal("3000.00"))
        self.assertEqual(commerce_summary()["purchase_total"], Decimal("3000.00"))

    def test_sales_order_total(self):
        order = SalesOrder.objects.create(number="VEN-001", customer=self.customer, date=date(2026, 7, 13))
        SalesOrderLine.objects.create(order=order, product=self.product, quantity=Decimal("3"), unit_price=Decimal("2500"))

        self.assertEqual(order.total_amount, Decimal("7500.00"))
        self.assertEqual(commerce_summary()["sales_total"], Decimal("7500.00"))


class CommerceRouteTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="comercio", password="test12345")
        for codename in ["access_commerce_module", "view_commerce_reports"]:
            permission = Permission.objects.get(codename=codename, content_type__app_label="Commerce")
            self.user.user_permissions.add(permission)

    def test_dashboard_requires_commerce_permission(self):
        self.client.login(username="comercio", password="test12345")
        response = self.client.get(reverse("commerce:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Compras y ventas")

    def test_reports_requires_report_permission(self):
        self.client.login(username="comercio", password="test12345")
        response = self.client.get(reverse("commerce:reports"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reportes comerciales")
