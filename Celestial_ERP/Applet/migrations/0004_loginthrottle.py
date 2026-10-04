from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("Applet", "0003_auditlog_changes_auditlog_object_id_and_more")]
    operations = [migrations.CreateModel(name="LoginThrottle", fields=[
        ("key", models.CharField(max_length=64, primary_key=True, serialize=False)),
        ("failures", models.PositiveIntegerField(default=0)),
        ("expires_at", models.DateTimeField(db_index=True)),
    ])]
