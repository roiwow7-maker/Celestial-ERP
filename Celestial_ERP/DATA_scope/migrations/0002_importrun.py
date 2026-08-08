from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("DATA_scope", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImportRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("started", "Iniciada"),
                            ("success", "Exitosa"),
                            ("failed", "Fallida"),
                        ],
                        default="started",
                        max_length=16,
                    ),
                ),
                ("transformed_path", models.CharField(max_length=500)),
                ("summaries_path", models.CharField(max_length=500)),
                ("descriptions_dir", models.CharField(blank=True, max_length=500)),
                ("transformed_sha256", models.CharField(blank=True, max_length=64)),
                ("summaries_sha256", models.CharField(blank=True, max_length=64)),
                ("clear_requested", models.BooleanField(default=False)),
                ("employee_count", models.PositiveIntegerField(default=0)),
                ("period_count", models.PositiveIntegerField(default=0)),
                ("item_count", models.PositiveIntegerField(default=0)),
                ("entry_count", models.PositiveIntegerField(default=0)),
                ("summary_count", models.PositiveIntegerField(default=0)),
                ("error_message", models.TextField(blank=True)),
            ],
            options={
                "db_table": "data_import_run",
                "ordering": ["-created_at"],
            },
        ),
    ]
