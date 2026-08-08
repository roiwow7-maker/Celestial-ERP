from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse


class ApiIndexTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="api_user", password="testpass123")
        self.client.login(username="api_user", password="testpass123")

    def test_api_index_renders_cascade_html(self):
        response = self.client.get(reverse("erp_api:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Celestial ERP API")
        self.assertContains(response, "Endpoints disponibles en cascada")
        self.assertContains(response, "api-accordion accordion")
        self.assertContains(response, "data-bs-parent=\"#apiAccordion\"")
        self.assertContains(response, "Salud")
        self.assertContains(response, "Estado del sistema")
        self.assertContains(response, "Restringida")

    def test_api_index_can_still_return_json(self):
        response = self.client.get(reverse("erp_api:index"), {"format": "json"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        payload = response.json()
        self.assertEqual(payload["name"], "Celestial ERP API")
        self.assertIn("health", payload["endpoints"])
        self.assertIn("payroll_summary", payload["endpoints"])

    def test_api_index_shows_restricted_samples_when_user_has_permission(self):
        content_type = ContentType.objects.get(app_label="DATA_scope", model="employee")
        permission = Permission.objects.get(
            codename="access_payroll_module",
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)

        response = self.client.get(reverse("erp_api:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resumen remuneraciones")
        self.assertContains(response, "Disponible")
        self.assertNotContains(response, "Requiere permiso DATA_scope.access_payroll_module")
