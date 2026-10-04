from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("Applet", "0004_loginthrottle")]
    operations = [migrations.CreateModel(name="CompanySettings", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("enabled_modules", models.JSONField(default=list)),
        ("updated_at", models.DateTimeField(auto_now=True)),
    ], options={"permissions": [("manage_company_modules", "Puede activar módulos de la empresa")]}),]
