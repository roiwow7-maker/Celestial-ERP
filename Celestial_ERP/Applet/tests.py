from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from Applet.audit import log_event
from DATA_scope.audit import log_manual_change
from DATA_scope.models import Employee

from Applet.models import AuditLog
from Applet.services import ensure_role_groups


class RoleAccessValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        ensure_role_groups()
        User = get_user_model()
        cls.users = {}
        for role_name in ["Administrador", "RRHH", "Contabilidad", "Solo lectura"]:
            user = User.objects.create_user(
                username=role_name.lower().replace(" ", "_"),
                password="test-password",
            )
            user.groups.add(Group.objects.get(name=role_name))
            cls.users[role_name] = user

    def login_as(self, role_name):
        self.client.force_login(self.users[role_name])

    def assert_get_status(self, route_name, expected_status, kwargs=None):
        response = self.client.get(reverse(route_name, kwargs=kwargs))
        self.assertEqual(response.status_code, expected_status, route_name)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("applet:home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_administrator_can_access_sensitive_modules(self):
        self.login_as("Administrador")
        for route_name in [
            "applet:home",
            "applet:admin_panel",
            "applet:security",
            "applet:audit",
            "applet:backups",
            "data_scope:payroll_dashboard",
            "data_scope:employees",
            "data_scope:periods",
            "data_scope:items",
            "data_scope:summaries",
            "data_scope:entries",
            "data_scope:reports",
            "data_scope:upload_data",
            "data_scope:export_reports_csv",
        ]:
            self.assert_get_status(route_name, 200)

    def test_rrhh_can_operate_payroll_but_not_security_or_backups(self):
        self.login_as("RRHH")
        for route_name in [
            "data_scope:payroll_dashboard",
            "data_scope:employees",
            "data_scope:periods",
            "data_scope:items",
            "data_scope:summaries",
            "data_scope:entries",
            "data_scope:reports",
            "data_scope:upload_data",
            "data_scope:export_reports_csv",
        ]:
            self.assert_get_status(route_name, 200)
        for route_name in ["applet:security", "applet:audit", "applet:backups"]:
            self.assert_get_status(route_name, 403)

    def test_accounting_can_read_and_export_but_not_upload(self):
        self.login_as("Contabilidad")
        for route_name in [
            "data_scope:payroll_dashboard",
            "data_scope:employees",
            "data_scope:periods",
            "data_scope:items",
            "data_scope:summaries",
            "data_scope:entries",
            "data_scope:reports",
            "data_scope:export_reports_csv",
        ]:
            self.assert_get_status(route_name, 200)
        self.assert_get_status("data_scope:upload_data", 403)
        self.assert_get_status("applet:security", 403)

    def test_read_only_can_read_payroll_but_not_export_or_upload(self):
        self.login_as("Solo lectura")
        for route_name in [
            "data_scope:payroll_dashboard",
            "data_scope:employees",
            "data_scope:periods",
            "data_scope:items",
            "data_scope:summaries",
            "data_scope:entries",
            "data_scope:reports",
        ]:
            self.assert_get_status(route_name, 200)
        self.assert_get_status("data_scope:export_reports_csv", 403)
        self.assert_get_status("data_scope:upload_data", 403)
        self.assert_get_status("applet:backups", 403)


class AuditGranularityTests(TestCase):
    def setUp(self):
        ensure_role_groups()
        User = get_user_model()
        self.admin = User.objects.create_user(username="audit_admin", password="test-password")
        self.admin.groups.add(Group.objects.get(name="Administrador"))

    def test_manual_change_stores_object_and_json_changes(self):
        employee = Employee.objects.create(codigo_ficha="A-1", rut="1-9", nombre="Auditado")
        before = {"nombre": "Auditado"}
        employee.nombre = "Auditado Nuevo"
        employee.save(update_fields=["nombre", "updated_at"])
        request = type("Request", (), {"user": self.admin})()

        log_manual_change(request, "employee_updated", employee, before)
        log = AuditLog.objects.get(action="employee_updated")

        self.assertEqual(log.object_type, "DATA_scope.employee")
        self.assertEqual(log.object_id, str(employee.pk))
        self.assertEqual(log.changes["nombre"]["old"], "Auditado")
        self.assertEqual(log.changes["nombre"]["new"], "Auditado Nuevo")

    def test_audit_view_filters_by_object_type(self):
        AuditLog.objects.create(module="DATA_scope", action="employee_updated", object_type="DATA_scope.employee", object_id="10")
        AuditLog.objects.create(module="DATA_scope", action="period_updated", object_type="DATA_scope.payrollperiod", object_id="20")
        self.client.login(username="audit_admin", password="test-password")

        response = self.client.get(reverse("applet:audit"), {"object_type": "employee"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "employee_updated")
        self.assertNotContains(response, "period_updated")

    def test_audit_event_is_traceable_to_nominal_user_and_role(self):
        rrhh_user = get_user_model().objects.create_user(username="rrhh_audit", password="test-password")
        rrhh_user.groups.add(Group.objects.get(name="RRHH"))
        request = type("Request", (), {"user": rrhh_user})()

        log_event(
            request,
            "role_trace_probe",
            "Applet",
            "Validacion de auditoria por usuario nominal y rol.",
            object_type="auth.user",
            object_id=rrhh_user.pk,
            object_repr=rrhh_user.username,
        )

        log = AuditLog.objects.get(action="role_trace_probe")
        self.assertEqual(log.user, rrhh_user)
        self.assertTrue(log.user.groups.filter(name="RRHH").exists())
        self.assertEqual(log.object_repr, "rrhh_audit")


class AdminInterfaceTests(TestCase):
    def test_admin_index_uses_simplified_custom_layout(self):
        User = get_user_model()
        user = User.objects.create_superuser(
            username="admin_ui",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Modulos administrables")
        self.assertContains(response, "erp-admin-app-list")
        self.assertContains(response, "Applet/css/admin_clean.css")
        self.assertContains(response, "Modo claro")
