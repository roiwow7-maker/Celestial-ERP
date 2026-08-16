from __future__ import annotations

import json
import secrets
import stat
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError

from Applet.services import ROLE_NAMES, ensure_role_groups, role_permissions


class Command(BaseCommand):
    help = "Crea o valida usuarios nominales desde un manifiesto privado y asigna un unico rol funcional."

    def add_arguments(self, parser):
        parser.add_argument("manifest", type=Path)
        parser.add_argument("--credentials-output", type=Path, default=None)
        parser.add_argument("--rotate-passwords", action="store_true")
        parser.add_argument(
            "--rotate-existing-superusers",
            action="store_true",
            help="Rota tambien las claves de superusuarios activos no incluidos en el manifiesto.",
        )
        parser.add_argument("--validate-only", action="store_true")

    def handle(self, *args, **options):
        manifest = options["manifest"]
        if not manifest.exists():
            raise CommandError(f"No existe manifiesto: {manifest}")
        records = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(records, list) or not records:
            raise CommandError("El manifiesto debe contener una lista no vacia.")
        if not options["validate_only"] and not options["credentials_output"]:
            raise CommandError("Usa --credentials-output para guardar claves temporales fuera de Git.")
        ensure_role_groups()
        User = get_user_model()
        credentials = []
        seen = set()
        for record in records:
            username = record.get("username", "").strip()
            email = record.get("email", "").strip()
            role = record.get("role", "").strip()
            if not username or not email or role not in ROLE_NAMES or username in seen:
                raise CommandError(f"Registro nominal invalido: {record}")
            seen.add(username)
            user = User.objects.filter(username=username).first()
            if options["validate_only"]:
                assigned_roles = set(user.groups.filter(name__in=ROLE_NAMES).values_list("name", flat=True)) if user else set()
                expected_staff = role == "Administrador"
                expected_permissions = {
                    f"{permission.content_type.app_label}.{permission.codename}"
                    for permission in role_permissions(role)
                }
                actual_permissions = user.get_all_permissions() if user else set()
                if (
                    not user
                    or not user.is_active
                    or user.is_superuser
                    or assigned_roles != {role}
                    or user.is_staff != expected_staff
                    or actual_permissions != expected_permissions
                ):
                    raise CommandError(f"Usuario no coincide con manifiesto: {username}")
                self.stdout.write(f"OK: {username} -> {role} ({len(expected_permissions)} permisos)")
                continue
            created = user is None
            if created:
                user = User(username=username, email=email, is_active=True)
            else:
                user.email = email
                user.is_active = True
            user.is_staff = role == "Administrador"
            password = None
            if created or options["rotate_passwords"]:
                password = secrets.token_urlsafe(18)
                user.set_password(password)
            user.save()
            user.groups.set([Group.objects.get(name=role)])
            if password:
                credentials.append({"username": username, "temporary_password": password})
            self.stdout.write(self.style.SUCCESS(f"Usuario {'creado' if created else 'actualizado'}: {username} -> {role}"))
        if options["rotate_existing_superusers"] and not options["validate_only"]:
            for user in User.objects.filter(is_superuser=True, is_active=True).exclude(username__in=seen):
                password = secrets.token_urlsafe(18)
                user.set_password(password)
                user.save(update_fields=["password"])
                credentials.append({
                    "username": user.username,
                    "temporary_password": password,
                    "reason": "superusuario existente rotado",
                })
                self.stdout.write(self.style.WARNING(f"Clave administrativa rotada: {user.username}"))
        if credentials:
            output = options["credentials_output"]
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(credentials, ensure_ascii=False, indent=2), encoding="utf-8")
            output.chmod(stat.S_IRUSR | stat.S_IWUSR)
            self.stdout.write(self.style.WARNING(f"Credenciales temporales (modo 600): {output}"))
