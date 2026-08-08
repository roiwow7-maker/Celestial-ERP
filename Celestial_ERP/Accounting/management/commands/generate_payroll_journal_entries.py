from django.core.management.base import BaseCommand, CommandError

from DATA_scope.models import PayrollPeriod
from Accounting.services import generate_payroll_journal_entry


class Command(BaseCommand):
    help = "Genera asiento contable de remuneraciones para un periodo."

    def add_arguments(self, parser):
        parser.add_argument("periodo", help="Periodo en formato AAAAMM.")
        parser.add_argument("--replace-existing", action="store_true", help="Reemplaza el asiento existente del periodo.")

    def handle(self, *args, **options):
        period = PayrollPeriod.objects.filter(periodo=options["periodo"]).first()
        if period is None:
            raise CommandError(f"No existe el periodo: {options['periodo']}")

        journal = generate_payroll_journal_entry(period, replace_existing=options["replace_existing"])
        self.stdout.write(self.style.SUCCESS(f"Asiento disponible: {journal.number}"))
        self.stdout.write(f"Debe: {journal.total_debit}")
        self.stdout.write(f"Haber: {journal.total_credit}")
        self.stdout.write(f"Cuadrado: {'si' if journal.is_balanced else 'no'}")
