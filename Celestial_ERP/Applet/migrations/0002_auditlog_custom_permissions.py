# Generated for Celestial ERP v0.4 access control.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Applet", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="auditlog",
            options={
                "ordering": ["-created_at"],
                "permissions": [
                    ("access_security_module", "Puede acceder al modulo de seguridad"),
                    ("access_admin_module", "Puede acceder al modulo de administracion"),
                    ("run_backups", "Puede ejecutar backups manuales"),
                ],
                "verbose_name": "Evento de auditoria",
                "verbose_name_plural": "Eventos de auditoria",
            },
        ),
    ]
