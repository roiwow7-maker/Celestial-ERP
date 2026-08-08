from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from DATA_scope.models import PayrollEntry, PayrollItem, PayrollPeriod

from .models import ChartAccount, CostCenter, JournalEntry, JournalEntryLine, PayrollItemAccountMapping


DEFAULT_ACCOUNTS = [
    ("1101", "Anticipos y cuentas por cobrar personal", ChartAccount.TYPE_ASSET),
    ("2101", "Remuneraciones por pagar", ChartAccount.TYPE_LIABILITY),
    ("2102", "Retenciones previsionales por pagar", ChartAccount.TYPE_LIABILITY),
    ("2103", "Otros descuentos por pagar", ChartAccount.TYPE_LIABILITY),
    ("5101", "Gasto haberes imponibles", ChartAccount.TYPE_EXPENSE),
    ("5102", "Gasto haberes no imponibles", ChartAccount.TYPE_EXPENSE),
    ("5103", "Gasto aportes empleador", ChartAccount.TYPE_EXPENSE),
    ("5104", "Gasto provisiones remuneraciones", ChartAccount.TYPE_EXPENSE),
    ("5199", "Gasto remuneraciones sin clasificar", ChartAccount.TYPE_EXPENSE),
]

DEFAULT_COST_CENTERS = [
    ("GEN", "General", "Centro de costo general para cargas historicas sin imputacion especifica."),
    ("RRHH", "RRHH", "Centro de costo administrativo para remuneraciones."),
]

CATEGORY_DEFAULTS = {
    PayrollItem.CATEGORY_HABERES_IMPONIBLES: ("5101", PayrollItemAccountMapping.MOVEMENT_DEBIT),
    PayrollItem.CATEGORY_HABERES_EXENTOS: ("5102", PayrollItemAccountMapping.MOVEMENT_DEBIT),
    PayrollItem.CATEGORY_ASIGNACIONES: ("5102", PayrollItemAccountMapping.MOVEMENT_DEBIT),
    PayrollItem.CATEGORY_CONTRIBUCION: ("5103", PayrollItemAccountMapping.MOVEMENT_DEBIT),
    PayrollItem.CATEGORY_PROVISIONES: ("5104", PayrollItemAccountMapping.MOVEMENT_DEBIT),
    PayrollItem.CATEGORY_DESCUENTOS_LEGALES: ("2102", PayrollItemAccountMapping.MOVEMENT_CREDIT),
    PayrollItem.CATEGORY_OTROS_DESCUENTOS: ("2103", PayrollItemAccountMapping.MOVEMENT_CREDIT),
    PayrollItem.CATEGORY_TOTALES: ("2101", PayrollItemAccountMapping.MOVEMENT_CREDIT),
}


def seed_accounting_catalog() -> dict[str, int]:
    account_count = 0
    for code, name, account_type in DEFAULT_ACCOUNTS:
        _, created = ChartAccount.objects.update_or_create(
            code=code,
            defaults={"name": name, "account_type": account_type, "is_active": True},
        )
        account_count += int(created)

    cost_center_count = 0
    for code, name, description in DEFAULT_COST_CENTERS:
        _, created = CostCenter.objects.update_or_create(
            code=code,
            defaults={"name": name, "description": description, "is_active": True},
        )
        cost_center_count += int(created)

    default_center = CostCenter.objects.get(code="GEN")
    mapping_count = 0
    accounts = {account.code: account for account in ChartAccount.objects.filter(code__in=[item[0] for item in DEFAULT_ACCOUNTS])}
    for item in PayrollItem.objects.all():
        default = CATEGORY_DEFAULTS.get(item.categoria)
        if not default:
            default = ("5199", PayrollItemAccountMapping.MOVEMENT_DEBIT)
        account_code, movement_type = default
        _, created = PayrollItemAccountMapping.objects.update_or_create(
            payroll_item=item,
            defaults={
                "account": accounts[account_code],
                "movement_type": movement_type,
                "cost_center": default_center,
                "is_active": True,
            },
        )
        mapping_count += int(created)

    return {
        "accounts_created": account_count,
        "cost_centers_created": cost_center_count,
        "mappings_created": mapping_count,
    }


def journal_number_for_period(period: PayrollPeriod) -> str:
    return f"REM-{period.periodo}"


def journal_date_for_period(period: PayrollPeriod) -> date:
    return date(period.year or 1900, period.month or 1, 1)


def payroll_mapping_gaps() -> list[PayrollItem]:
    return list(PayrollItem.objects.filter(account_mapping__isnull=True).order_by("categoria", "codigo"))


@transaction.atomic
def generate_payroll_journal_entry(period: PayrollPeriod, replace_existing: bool = False) -> JournalEntry:
    number = journal_number_for_period(period)
    existing = JournalEntry.objects.filter(number=number).first()
    if existing and not replace_existing:
        return existing
    if existing and replace_existing:
        existing.delete()

    mapped_entries = (
        PayrollEntry.objects.filter(period=period, item__account_mapping__is_active=True)
        .select_related("item__account_mapping__account", "item__account_mapping__cost_center")
    )

    grouped: dict[tuple[int, int | None, str, str], Decimal] = defaultdict(Decimal)
    for entry in mapped_entries:
        mapping = entry.item.account_mapping
        key = (
            mapping.account_id,
            mapping.cost_center_id,
            mapping.movement_type,
            f"{mapping.account.code} - {mapping.account.name}",
        )
        grouped[key] += entry.monto or Decimal("0")

    journal = JournalEntry.objects.create(
        period=period,
        number=number,
        date=journal_date_for_period(period),
        description=f"Asiento de remuneraciones {period.periodo}",
        source=JournalEntry.SOURCE_PAYROLL,
        status=JournalEntry.STATUS_DRAFT,
    )

    for (account_id, cost_center_id, movement_type, description), amount in sorted(grouped.items(), key=lambda item: item[0][3]):
        if amount == 0:
            continue
        debit = amount if movement_type == PayrollItemAccountMapping.MOVEMENT_DEBIT else Decimal("0")
        credit = amount if movement_type == PayrollItemAccountMapping.MOVEMENT_CREDIT else Decimal("0")
        JournalEntryLine.objects.create(
            journal_entry=journal,
            account_id=account_id,
            cost_center_id=cost_center_id,
            description=description,
            debit=abs(debit),
            credit=abs(credit),
        )

    difference = journal.difference
    if difference:
        payable_account, _ = ChartAccount.objects.get_or_create(
            code="2101",
            defaults={
                "name": "Remuneraciones por pagar",
                "account_type": ChartAccount.TYPE_LIABILITY,
                "is_active": True,
            },
        )
        if difference > 0:
            debit = Decimal("0")
            credit = difference
        else:
            debit = abs(difference)
            credit = Decimal("0")
        JournalEntryLine.objects.create(
            journal_entry=journal,
            account=payable_account,
            cost_center=CostCenter.objects.filter(code="GEN").first(),
            description="Contrapartida automatica remuneraciones por pagar",
            debit=debit,
            credit=credit,
        )

    return journal


def accounting_report_summary() -> dict[str, object]:
    line_totals = JournalEntryLine.objects.aggregate(total_debit=Sum("debit"), total_credit=Sum("credit"))
    return {
        "accounts": ChartAccount.objects.count(),
        "cost_centers": CostCenter.objects.count(),
        "mappings": PayrollItemAccountMapping.objects.count(),
        "mapping_gaps": len(payroll_mapping_gaps()),
        "journal_entries": JournalEntry.objects.count(),
        "journal_lines": JournalEntryLine.objects.count(),
        "total_debit": line_totals["total_debit"] or Decimal("0"),
        "total_credit": line_totals["total_credit"] or Decimal("0"),
    }


def account_balances():
    rows = (
        JournalEntryLine.objects.values("account__code", "account__name", "account__account_type")
        .annotate(total_debit=Sum("debit"), total_credit=Sum("credit"))
        .order_by("account__code")
    )
    balances = []
    for row in rows:
        total_debit = row["total_debit"] or Decimal("0")
        total_credit = row["total_credit"] or Decimal("0")
        row["balance"] = total_debit - total_credit
        balances.append(row)
    return balances
