from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from DATA_scope.models import Employee


class AttendanceTimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AttendanceRecord(AttendanceTimeStampedModel):
    STATUS_PRESENT = "present"
    STATUS_ABSENT = "absent"
    STATUS_LATE = "late"
    STATUS_LEAVE = "leave"
    STATUS_HOLIDAY = "holiday"
    STATUS_REMOTE = "remote"

    STATUS_CHOICES = [
        (STATUS_PRESENT, "Presente"),
        (STATUS_ABSENT, "Ausente"),
        (STATUS_LATE, "Atraso"),
        (STATUS_LEAVE, "Permiso/Licencia"),
        (STATUS_HOLIDAY, "Feriado"),
        (STATUS_REMOTE, "Remoto"),
    ]

    SOURCE_MANUAL = "manual"
    SOURCE_IMPORT = "import"
    SOURCE_DEVICE = "device"

    SOURCE_CHOICES = [
        (SOURCE_MANUAL, "Manual"),
        (SOURCE_IMPORT, "Importacion"),
        (SOURCE_DEVICE, "Reloj control"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="attendance_records")
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    break_minutes = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "attendance_record"
        ordering = ["-date", "employee__nombre"]
        verbose_name = "Registro de asistencia"
        verbose_name_plural = "Registros de asistencia"
        constraints = [
            models.UniqueConstraint(fields=["employee", "date"], name="attendance_unique_employee_date"),
        ]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["employee", "date"]),
            models.Index(fields=["status"]),
        ]
        permissions = [
            ("access_attendance_module", "Puede acceder al modulo de asistencia"),
            ("manage_attendance_records", "Puede administrar registros de asistencia"),
            ("view_attendance_reports", "Puede ver reportes de asistencia"),
            ("export_attendance_reports", "Puede exportar reportes de asistencia"),
        ]

    @property
    def worked_minutes(self) -> int:
        if not self.check_in or not self.check_out:
            return 0
        start = datetime.combine(self.date, self.check_in)
        end = datetime.combine(self.date, self.check_out)
        if end < start:
            end += timedelta(days=1)
        minutes = int((end - start).total_seconds() // 60) - int(self.break_minutes or 0)
        return max(minutes, 0)

    @property
    def worked_hours(self) -> Decimal:
        return (Decimal(self.worked_minutes) / Decimal("60")).quantize(Decimal("0.01"))

    def clean(self):
        if self.status in {self.STATUS_PRESENT, self.STATUS_LATE, self.STATUS_REMOTE} and not (self.check_in and self.check_out):
            raise ValidationError("Los estados con jornada trabajada requieren hora de entrada y salida.")
        if self.break_minutes and self.worked_minutes == 0 and self.check_in and self.check_out:
            raise ValidationError("El descanso no puede dejar la jornada en cero.")

    def __str__(self) -> str:
        return f"{self.employee.codigo_ficha} {self.date} {self.get_status_display()}"
