from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from DATA_scope.models import PayrollItem, PayrollPeriod


class AccountingTimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ChartAccount(AccountingTimeStampedModel):
    TYPE_ASSET = "asset"
    TYPE_LIABILITY = "liability"
    TYPE_EQUITY = "equity"
    TYPE_INCOME = "income"
    TYPE_EXPENSE = "expense"

    TYPE_CHOICES = [
        (TYPE_ASSET, "Activo"),
        (TYPE_LIABILITY, "Pasivo"),
        (TYPE_EQUITY, "Patrimonio"),
        (TYPE_INCOME, "Ingreso"),
        (TYPE_EXPENSE, "Gasto"),
    ]

    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=180)
    account_type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="children")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "accounting_chart_account"
        ordering = ["code"]
        verbose_name = "Cuenta contable"
        verbose_name_plural = "Plan de cuentas"
        permissions = [
            ("access_accounting_module", "Puede acceder al modulo de contabilidad"),
            ("manage_accounting_config", "Puede administrar configuracion contable"),
            ("generate_journal_entries", "Puede generar asientos contables"),
            ("view_accounting_reports", "Puede ver reportes contables"),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class CostCenter(AccountingTimeStampedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "accounting_cost_center"
        ordering = ["code"]
        verbose_name = "Centro de costo"
        verbose_name_plural = "Centros de costo"

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class PayrollItemAccountMapping(AccountingTimeStampedModel):
    MOVEMENT_DEBIT = "debit"
    MOVEMENT_CREDIT = "credit"

    MOVEMENT_CHOICES = [
        (MOVEMENT_DEBIT, "Debe"),
        (MOVEMENT_CREDIT, "Haber"),
    ]

    payroll_item = models.OneToOneField(PayrollItem, on_delete=models.CASCADE, related_name="account_mapping")
    account = models.ForeignKey(ChartAccount, on_delete=models.PROTECT, related_name="payroll_mappings")
    movement_type = models.CharField(max_length=8, choices=MOVEMENT_CHOICES)
    cost_center = models.ForeignKey(CostCenter, null=True, blank=True, on_delete=models.PROTECT, related_name="payroll_mappings")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "accounting_payroll_item_mapping"
        ordering = ["payroll_item__categoria", "payroll_item__codigo"]
        verbose_name = "Mapeo item-cuenta"
        verbose_name_plural = "Mapeos item-cuenta"

    def __str__(self) -> str:
        return f"{self.payroll_item.codigo} -> {self.account.code} ({self.movement_type})"


class JournalEntry(AccountingTimeStampedModel):
    SOURCE_PAYROLL = "payroll"
    SOURCE_MANUAL = "manual"

    SOURCE_CHOICES = [
        (SOURCE_PAYROLL, "Remuneraciones"),
        (SOURCE_MANUAL, "Manual"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_POSTED = "posted"
    STATUS_VOID = "void"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Borrador"),
        (STATUS_POSTED, "Contabilizado"),
        (STATUS_VOID, "Anulado"),
    ]

    period = models.ForeignKey(PayrollPeriod, on_delete=models.PROTECT, related_name="journal_entries")
    number = models.CharField(max_length=80, unique=True)
    date = models.DateField()
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default=SOURCE_PAYROLL)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    class Meta:
        db_table = "accounting_journal_entry"
        ordering = ["-date", "-id"]
        verbose_name = "Asiento contable"
        verbose_name_plural = "Asientos contables"

    def __str__(self) -> str:
        return self.number

    @property
    def total_debit(self) -> Decimal:
        return self.lines.aggregate(total=models.Sum("debit"))["total"] or Decimal("0")

    @property
    def total_credit(self) -> Decimal:
        return self.lines.aggregate(total=models.Sum("credit"))["total"] or Decimal("0")

    @property
    def difference(self) -> Decimal:
        return self.total_debit - self.total_credit

    @property
    def is_balanced(self) -> bool:
        return self.difference == 0


class JournalEntryLine(AccountingTimeStampedModel):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="lines")
    account = models.ForeignKey(ChartAccount, on_delete=models.PROTECT, related_name="journal_lines")
    cost_center = models.ForeignKey(CostCenter, null=True, blank=True, on_delete=models.PROTECT, related_name="journal_lines")
    description = models.CharField(max_length=255, blank=True)
    debit = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    credit = models.DecimalField(max_digits=16, decimal_places=0, default=0)

    class Meta:
        db_table = "accounting_journal_entry_line"
        ordering = ["journal_entry", "id"]
        verbose_name = "Linea de asiento"
        verbose_name_plural = "Lineas de asiento"
        indexes = [
            models.Index(fields=["account"]),
            models.Index(fields=["cost_center"]),
        ]

    def clean(self):
        if self.debit and self.credit:
            raise ValidationError("Una linea no puede tener Debe y Haber al mismo tiempo.")
        if not self.debit and not self.credit:
            raise ValidationError("Una linea debe tener monto en Debe o Haber.")

    def __str__(self) -> str:
        amount = self.debit or self.credit
        side = "D" if self.debit else "H"
        return f"{self.journal_entry.number} {self.account.code} {side} {amount}"
