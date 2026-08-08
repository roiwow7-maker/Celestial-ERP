from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from Applet.services import ROLE_NAMES, ensure_role_groups


class Command(BaseCommand):
    help = "Crea grupos base de acceso para operar el ERP sin compartir superusuario."

    def add_arguments(self, parser):
        parser.add_argument("--admin-user", default="admin", help="Usuario superadmin local a asociar al rol administrador.")
        parser.add_argument("--admin-password", default="", help="Nueva clave para el usuario admin local.")

    def handle(self, *args, **options):
        groups = ensure_role_groups()
        for group in groups:
            self.stdout.write(f"Rol actualizado: {group.name} ({group.permissions.count()} permisos)")

        User = get_user_model()
        username = options["admin_user"]
        admin_user = User.objects.filter(username=username).first()
        if admin_user:
            admin_group = Group.objects.get(name="Administrador")
            admin_user.groups.add(admin_group)
            admin_user.is_staff = True
            if options["admin_password"]:
                admin_user.set_password(options["admin_password"])
                admin_user.save(update_fields=["password", "is_staff"])
                self.stdout.write(self.style.SUCCESS(f"Clave actualizada para usuario: {username}"))
            else:
                admin_user.save(update_fields=["is_staff"])
            self.stdout.write(self.style.SUCCESS(f"Usuario {username} asociado a Administrador"))
        else:
            self.stdout.write(self.style.WARNING(f"No existe el usuario {username}; crea usuarios nominales desde admin."))
        self.stdout.write(self.style.SUCCESS(f"Roles disponibles: {', '.join(ROLE_NAMES)}"))
