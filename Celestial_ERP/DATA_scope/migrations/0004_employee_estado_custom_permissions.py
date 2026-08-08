# Generated for Celestial ERP v0.4 access control.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Applet", "0001_initial"),
        ("DATA_scope", "0003_alter_employee_options_alter_importrun_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="estado",
            field=models.CharField(
                choices=[
                    ("active", "Activo"),
                    ("inactive", "Inactivo"),
                    ("terminated", "Finiquitado"),
                    ("pending_review", "Pendiente revision"),
                ],
                default="active",
                max_length=24,
            ),
        ),
        migrations.AlterModelOptions(
            name="employee",
            options={
                "ordering": ["nombre", "codigo_ficha"],
                "permissions": [
                    ("access_payroll_module", "Puede acceder al modulo de remuneraciones"),
                    ("manage_employee_status", "Puede cambiar estados de trabajadores"),
                ],
                "verbose_name": "Trabajador",
                "verbose_name_plural": "Trabajadores",
            },
        ),
        migrations.AlterModelOptions(
            name="importrun",
            options={
                "ordering": ["-created_at"],
                "permissions": [
                    ("upload_payroll_data", "Puede cargar archivos de remuneraciones"),
                    ("import_payroll_data", "Puede importar datos al ERP"),
                    ("clear_payroll_data", "Puede limpiar datos antes de importar"),
                    ("download_upload_output", "Puede descargar salidas de cargas ETL"),
                ],
                "verbose_name": "Carga ETL",
                "verbose_name_plural": "Cargas ETL",
            },
        ),
    ]
