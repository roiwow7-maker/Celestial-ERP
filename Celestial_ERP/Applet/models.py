from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=80)
    module = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    object_type = models.CharField(max_length=120, blank=True)
    object_id = models.CharField(max_length=80, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Evento de auditoria"
        verbose_name_plural = "Eventos de auditoria"
        indexes = [
            models.Index(fields=["module", "action"]),
            models.Index(fields=["object_type", "object_id"]),
            models.Index(fields=["created_at"]),
        ]
        permissions = [
            ("access_security_module", "Puede acceder al modulo de seguridad"),
            ("access_admin_module", "Puede acceder al modulo de administracion"),
            ("run_backups", "Puede ejecutar backups manuales"),
        ]

    def __str__(self) -> str:
        return f"{self.created_at:%Y-%m-%d %H:%M:%S} - {self.module} - {self.action}"


class LoginThrottle(models.Model):
    """Contadores por empresa compartidos por todos sus workers; sin credenciales."""
    key = models.CharField(max_length=64, primary_key=True)
    failures = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(db_index=True)


class CompanySettings(models.Model):
    enabled_modules = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [("manage_company_modules", "Puede activar módulos de la empresa")]
