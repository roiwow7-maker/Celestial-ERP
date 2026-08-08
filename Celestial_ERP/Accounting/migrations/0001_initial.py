from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("DATA_scope", "0004_employee_estado_custom_permissions"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChartAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=32, unique=True)),
                ("name", models.CharField(max_length=180)),
                ("account_type", models.CharField(choices=[("asset", "Activo"), ("liability", "Pasivo"), ("equity", "Patrimonio"), ("income", "Ingreso"), ("expense", "Gasto")], max_length=16)),
                ("is_active", models.BooleanField(default=True)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="children", to="Accounting.chartaccount")),
            ],
            options={
                "verbose_name": "Cuenta contable",
                "verbose_name_plural": "Plan de cuentas",
                "db_table": "accounting_chart_account",
                "ordering": ["code"],
                "permissions": [("access_accounting_module", "Puede acceder al modulo de contabilidad"), ("manage_accounting_config", "Puede administrar configuracion contable"), ("generate_journal_entries", "Puede generar asientos contables"), ("view_accounting_reports", "Puede ver reportes contables")],
            },
        ),
        migrations.CreateModel(
            name="CostCenter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=32, unique=True)),
                ("name", models.CharField(max_length=160)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Centro de costo",
                "verbose_name_plural": "Centros de costo",
                "db_table": "accounting_cost_center",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="JournalEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("number", models.CharField(max_length=80, unique=True)),
                ("date", models.DateField()),
                ("description", models.CharField(max_length=255)),
                ("source", models.CharField(choices=[("payroll", "Remuneraciones"), ("manual", "Manual")], default="payroll", max_length=16)),
                ("status", models.CharField(choices=[("draft", "Borrador"), ("posted", "Contabilizado"), ("void", "Anulado")], default="draft", max_length=16)),
                ("period", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="journal_entries", to="DATA_scope.payrollperiod")),
            ],
            options={
                "verbose_name": "Asiento contable",
                "verbose_name_plural": "Asientos contables",
                "db_table": "accounting_journal_entry",
                "ordering": ["-date", "-id"],
            },
        ),
        migrations.CreateModel(
            name="PayrollItemAccountMapping",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("movement_type", models.CharField(choices=[("debit", "Debe"), ("credit", "Haber")], max_length=8)),
                ("is_active", models.BooleanField(default=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payroll_mappings", to="Accounting.chartaccount")),
                ("cost_center", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="payroll_mappings", to="Accounting.costcenter")),
                ("payroll_item", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="account_mapping", to="DATA_scope.payrollitem")),
            ],
            options={
                "verbose_name": "Mapeo item-cuenta",
                "verbose_name_plural": "Mapeos item-cuenta",
                "db_table": "accounting_payroll_item_mapping",
                "ordering": ["payroll_item__categoria", "payroll_item__codigo"],
            },
        ),
        migrations.CreateModel(
            name="JournalEntryLine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("debit", models.DecimalField(decimal_places=0, default=0, max_digits=16)),
                ("credit", models.DecimalField(decimal_places=0, default=0, max_digits=16)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="journal_lines", to="Accounting.chartaccount")),
                ("cost_center", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="journal_lines", to="Accounting.costcenter")),
                ("journal_entry", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lines", to="Accounting.journalentry")),
            ],
            options={
                "verbose_name": "Linea de asiento",
                "verbose_name_plural": "Lineas de asiento",
                "db_table": "accounting_journal_entry_line",
                "ordering": ["journal_entry", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="journalentryline",
            index=models.Index(fields=["account"], name="accounting__account_c3f49f_idx"),
        ),
        migrations.AddIndex(
            model_name="journalentryline",
            index=models.Index(fields=["cost_center"], name="accounting__cost_ce_01066c_idx"),
        ),
    ]
