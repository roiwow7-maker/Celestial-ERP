"""Crea la primera cuenta nominal sin transmitir contraseñas por argumentos."""
import json
import os
import secrets
from pathlib import Path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from Applet.services import ensure_role_groups


class Command(BaseCommand):
    help = "Crea el administrador inicial de una empresa vacía y guarda la credencial en un archivo privado."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--credential-file", required=True, type=Path)

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.exists():
            raise CommandError("La empresa ya tiene usuarios; utiliza la administración de cuentas existente.")
        path = options["credential_file"].resolve()
        password = secrets.token_urlsafe(24)
        with transaction.atomic():
            ensure_role_groups()
            user = User.objects.create_user(username=options["username"], password=password, is_staff=True)
            user.groups.add(Group.objects.get(name="Administrador"))
            # Fallar antes del commit si el destino existe o no permite guardar la credencial.
            with open(path, "x", encoding="utf-8", opener=lambda name, flags: os.open(name, flags, 0o600)) as handle:
                json.dump({"company": settings.ERP_COMPANY_ID, "username": user.username, "password": password}, handle, indent=2)
        self.stdout.write(f"Cuenta inicial creada. Credencial privada: {path}")
