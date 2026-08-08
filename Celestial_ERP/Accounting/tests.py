from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from DATA_scope.models import Employee, PayrollEntry, PayrollItem, PayrollPeriod

from .models import ChartAccount, JournalEntry, PayrollItemAccountMapping
from .services import generate_payroll_journal_entry, seed_accounting_catalog


class AccountingCatalogTests(TestCase):
    def setUp(self):
        self.period = PayrollPeriod.objects.create(periodo="202606", year=2026, month=6)
        self.employee = Employee.objects.create(codigo_ficha="100", rut="1-9", nombre="Trabajador Demo")
        self.item = PayrollItem.objects.create(
            codigo="SUBASE",
            categoria=PayrollItem.CATEGORY_HABERES_IMPONIBLES,
            descripcion="Sueldo base",
        )
        PayrollEntry.objects.create(employee=self.employee, period=self.period, item=self.item, monto=Decimal("1000"))

    def test_seed_catalog_creates_accounts_and_mapping(self):
        result = seed_accounting_catalog()

        self.assertGreaterEqual(result["accounts_created"], 1)
        self.assertTrue(ChartAccount.objects.filter(code="5101").exists())
        self.assertTrue(PayrollItemAccountMapping.objects.filter(payroll_item=self.item).exists())

    def test_generate_payroll_journal_entry_balances_with_payable_counterpart(self):
        seed_accounting_catalog()

        journal = generate_payroll_journal_entry(self.period)

        self.assertEqual(journal.number, "REM-202606")
        self.assertEqual(journal.lines.count(), 2)
        self.assertEqual(journal.total_debit, Decimal("1000"))
        self.assertEqual(journal.total_credit, Decimal("1000"))
        self.assertTrue(journal.is_balanced)


class AccountingRouteTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="conta", password="test-password")
        permission = Permission.objects.get(codename="access_accounting_module", content_type__app_label="Accounting")
        self.user.user_permissions.add(permission)
        self.client = Client()
        self.client.login(username="conta", password="test-password")

    def test_dashboard_requires_accounting_permission_and_renders(self):
        response = self.client.get(reverse("accounting:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contabilidad")
