from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from Attendance.payroll_sync import sync_attendance_to_payroll
from DATA_scope.models import PayrollPeriod


class Command(BaseCommand):
    help = "Sincroniza asistencia mensual hacia dias, ausencias y horas no trabajadas de liquidaciones."

    def add_arguments(self, parser):
        parser.add_argument("periodo", help="Periodo en formato AAAAMM.")
        parser.add_argument("--dry-run", action="store_true", help="Calcula cambios sin guardar.")
        parser.add_argument("--hours-per-absence", default="8.00", help="Horas no trabajadas por dia ausente.")

    def handle(self, *args, **options):
        period_code = options["periodo"].strip()
        if len(period_code) != 6 or not period_code.isdigit():
            raise CommandError("El periodo debe usar formato AAAAMM.")
        if not PayrollPeriod.objects.filter(periodo=period_code).exists():
            raise CommandError(f"No existe el periodo {period_code}.")

        hours_per_absence = Decimal(options["hours_per_absence"])
        rows = sync_attendance_to_payroll(
            period_code,
            dry_run=options["dry_run"],
            hours_per_absence=hours_per_absence,
        )
        changed = sum(1 for row in rows if row.changed)
        mode = "simulacion" if options["dry_run"] else "aplicado"
        self.stdout.write(self.style.SUCCESS(f"Sincronizacion {mode}: {changed}/{len(rows)} liquidaciones con cambios."))
        for row in rows[:20]:
            if row.changed:
                self.stdout.write(
                    f"- {row.summary.document_number}: dias={row.worked_days}, "
                    f"ausencias={row.absence_days}, permisos={row.leave_days}, "
                    f"horas_no_trabajadas={row.not_worked_hours}"
                )
