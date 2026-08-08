from django.core.management.base import BaseCommand

from Accounting.services import seed_accounting_catalog


class Command(BaseCommand):
    help = "Crea plan de cuentas base, centros de costo base y mapeos iniciales desde items de remuneracion."

    def handle(self, *args, **options):
        result = seed_accounting_catalog()
        self.stdout.write(self.style.SUCCESS("Catalogo contable preparado."))
        self.stdout.write(f"Cuentas creadas: {result['accounts_created']}")
        self.stdout.write(f"Centros creados: {result['cost_centers_created']}")
        self.stdout.write(f"Mapeos creados: {result['mappings_created']}")
