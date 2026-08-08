from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


TEMPORARY_PASSWORDS = ["root", "admin", "password", "123456", "test", "test-password"]


class Command(BaseCommand):
    help = "Revisa configuracion sensible, credenciales nominales y riesgos operativos basicos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fail-on-warning",
            action="store_true",
            help="Retorna error si existen advertencias operativas.",
        )

    def handle(self, *args, **options):
        warnings: list[str] = []
        ok: list[str] = []

        environment = getattr(settings, "ERP_SETTINGS_ENV", "dev")
        ok.append(f"Entorno activo: {environment}")

        if settings.DEBUG:
            warnings.append("DJANGO_DEBUG esta activo. No usar asi en red compartida.")
        else:
            ok.append("DJANGO_DEBUG desactivado.")

        secret_key = settings.SECRET_KEY
        if secret_key.startswith("django-local-"):
            warnings.append("DJANGO_SECRET_KEY usa clave local generada. Define una clave explicita para uso compartido.")
        elif "change-this" in secret_key.lower():
            warnings.append("DJANGO_SECRET_KEY parece mantener valor de ejemplo.")
        else:
            ok.append("DJANGO_SECRET_KEY no parece temporal.")

        allowed_hosts = list(settings.ALLOWED_HOSTS)
        if not allowed_hosts:
            warnings.append("DJANGO_ALLOWED_HOSTS esta vacio.")
        elif "*" in allowed_hosts:
            warnings.append("DJANGO_ALLOWED_HOSTS contiene '*'. Evitarlo en operacion real.")
        else:
            ok.append(f"ALLOWED_HOSTS configurado: {', '.join(allowed_hosts)}")

        if not settings.SESSION_COOKIE_SECURE and not settings.DEBUG:
            warnings.append("SESSION_COOKIE_SECURE desactivado fuera de DEBUG.")
        if not settings.CSRF_COOKIE_SECURE and not settings.DEBUG:
            warnings.append("CSRF_COOKIE_SECURE desactivado fuera de DEBUG.")

        User = get_user_model()
        active_users = User.objects.filter(is_active=True)
        if not active_users.exists():
            warnings.append("No hay usuarios activos.")
        else:
            ok.append(f"Usuarios activos: {active_users.count()}")

        risky_users = []
        for user in active_users:
            for password in TEMPORARY_PASSWORDS:
                if user.check_password(password):
                    risky_users.append(f"{user.username}/{password}")
                    break
        if risky_users:
            warnings.append("Usuarios con clave temporal conocida: " + ", ".join(risky_users))
        else:
            ok.append("No se detectaron claves temporales conocidas.")

        staff_without_groups = active_users.filter(is_staff=True, groups__isnull=True).distinct()
        if staff_without_groups.exists():
            warnings.append(
                "Usuarios staff sin rol/grupo nominal: "
                + ", ".join(staff_without_groups.values_list("username", flat=True))
            )
        else:
            ok.append("Usuarios staff asociados a grupos o sin staff activo sin rol.")

        self.stdout.write(self.style.SUCCESS("Checks correctos:"))
        for message in ok:
            self.stdout.write(f"- {message}")

        if warnings:
            self.stdout.write(self.style.WARNING("\nAdvertencias:"))
            for message in warnings:
                self.stdout.write(f"- {message}")
            if options["fail_on_warning"]:
                raise SystemExit(1)
            return

        self.stdout.write(self.style.SUCCESS("\nSin advertencias operativas."))
