import json
import time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase, override_settings
from django.urls import reverse

from Applet.models import AuditLog
from Applet.services import ensure_role_groups
from Inventory.models import Product, Warehouse, StockMovement, StockBalance
from Inventory.services import apply_stock_movement


class SecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        ensure_role_groups()
        cls.admin = get_user_model().objects.create_superuser("owner", password="Distant!River2026")
        cls.other = get_user_model().objects.create_user("reader", password="Distant!River2026")

    def setUp(self):
        self.client.force_login(self.admin)

    def patch(self, user, data):
        return self.client.patch(reverse("erp_api:v1_user_detail", args=[user.pk]), json.dumps(data), content_type="application/json")

    def test_cannot_disable_own_account_with_actual_frontend_field(self):
        result = self.patch(self.admin, {"is_active": False})
        self.assertEqual(result.status_code, 400)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_weak_password_rejected_without_partial_user_update(self):
        result = self.patch(self.other, {"is_active": False, "password": "123"})
        self.assertEqual(result.status_code, 400)
        self.other.refresh_from_db()
        self.assertTrue(self.other.is_active)
        self.assertTrue(self.other.check_password("Distant!River2026"))

    def test_module_access_does_not_allow_user_mutations(self):
        self.other.user_permissions.add(Permission.objects.get(codename="access_security_module"))
        self.client.force_login(self.other)
        result = self.patch(self.admin, {"password": "Different!River2026"})
        self.assertEqual(result.status_code, 403)

    def test_company_admin_cannot_edit_superuser(self):
        self.other.groups.add(Group.objects.get(name="Administrador"))
        self.client.force_login(self.other)
        self.assertEqual(self.patch(self.admin, {"is_active": False}).status_code, 403)

    def test_unknown_roles_and_boolean_strings_rejected(self):
        self.assertEqual(self.patch(self.other, {"roles": ["not-a-role"]}).status_code, 400)
        self.assertEqual(self.patch(self.other, {"is_active": "false"}).status_code, 400)

    def test_audit_does_not_store_password(self):
        secret = "Different!River2026"
        self.assertEqual(self.patch(self.other, {"password": secret}).status_code, 200)
        event = AuditLog.objects.get(action="user_updated")
        self.assertTrue(event.changes["password_changed"])
        self.assertNotIn(secret, json.dumps(event.changes))

    def test_invalid_json_shapes_return_bad_request(self):
        for payload in ["[]", "null", '"text"', "{broken"]:
            result = self.client.patch(reverse("erp_api:v1_user_detail", args=[self.other.pk]), payload, content_type="application/json")
            self.assertEqual(result.status_code, 400)

    @override_settings(ERP_SESSION_IDLE_SECONDS=30)
    def test_idle_session_expires(self):
        session = self.client.session
        session["erp_last_seen"] = int(time.time()) - 60
        session.save()
        result = self.client.get(reverse("erp_api:v1_session"))
        self.assertFalse(result.json()["authenticated"])
        self.assertEqual(result.headers["Cache-Control"], "no-store, private")

    @override_settings(ERP_LOGIN_ATTEMPTS=2)
    def test_failed_logins_are_throttled_across_clients(self):
        from django.test import Client
        self.client.logout()
        url = reverse("erp_api:v1_login")
        for _ in range(2):
            result = self.client.post(url, {"username": "owner", "password": "incorrect"}, content_type="application/json")
            self.assertEqual(result.status_code, 400)
        result = Client().post(url, {"username": "owner", "password": "Distant!River2026"}, content_type="application/json")
        self.assertEqual(result.status_code, 429)
        self.assertIn("Retry-After", result.headers)

    @override_settings(ERP_COMPANY_ID="company-a", ERP_COMPANY_NAME="Company A")
    def test_session_identifies_company_without_database_credentials(self):
        result = self.client.get(reverse("erp_api:v1_session"))
        self.assertEqual(result.json()["company"], {"id": "company-a", "name": "Company A"})
        self.assertEqual(result.headers["X-ERP-Company"], "company-a")
        self.assertNotIn("PASSWORD", result.content.decode())

    def test_applied_stock_movement_cannot_be_edited(self):
        product = Product.objects.create(sku="SAFE", name="Product")
        warehouse = Warehouse.objects.create(code="SAFE", name="Warehouse")
        movement = apply_stock_movement(StockMovement(product=product, warehouse=warehouse, movement_type="in", date="2026-09-27", quantity=Decimal("10"), unit_cost=Decimal("2")))
        result = self.client.put(reverse("erp_api:v1_resource_detail", args=["stock-movements", movement.pk]), {"product": product.pk, "warehouse": warehouse.pk, "movement_type": "in", "date": "2026-09-27", "quantity": "20", "unit_cost": "2"}, content_type="application/json")
        self.assertEqual(result.status_code, 409)
        movement.refresh_from_db()
        self.assertEqual(movement.quantity, 10)
        self.assertEqual(StockBalance.objects.get(product=product, warehouse=warehouse).quantity, 10)

    def test_insufficient_stock_returns_validation_error_and_no_movement(self):
        product = Product.objects.create(sku="EMPTY", name="Product")
        warehouse = Warehouse.objects.create(code="EMPTY", name="Warehouse")
        result = self.client.post(reverse("erp_api:v1_resource_collection", args=["stock-movements"]), {"product": product.pk, "warehouse": warehouse.pk, "movement_type": "out", "date": "2026-09-27", "quantity": "1", "unit_cost": "2"}, content_type="application/json")
        self.assertEqual(result.status_code, 400)
        self.assertFalse(StockMovement.objects.exists())
