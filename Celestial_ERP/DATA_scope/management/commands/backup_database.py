from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Ejecuta el respaldo apropiado para la base configurada."

    def handle(self, *args, **options):
        engine = settings.DATABASES["default"]["ENGINE"]
        if engine == "django.db.backends.postgresql":
            call_command("backup_postgresql", stdout=self.stdout, stderr=self.stderr)
            return
        if engine == "django.db.backends.sqlite3":
            call_command("backup_sqlite", stdout=self.stdout, stderr=self.stderr)
            return
        raise CommandError(f"No existe estrategia de backup para {engine}.")

