from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Employee(TimeStampedModel):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_TERMINATED = "terminated"
    STATUS_PENDING_REVIEW = "pending_review"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Activo"),
        (STATUS_INACTIVE, "Inactivo"),
        (STATUS_TERMINATED, "Finiquitado"),
        (STATUS_PENDING_REVIEW, "Pendiente revision"),
    ]

    codigo_ficha = models.CharField(max_length=32, unique=True)
    rut = models.CharField(max_length=32, blank=True)
    nombre = models.CharField(max_length=255)
    estado = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    division = models.CharField(max_length=120, blank=True)
    afp = models.CharField(max_length=80, blank=True)
    isapre = models.CharField(max_length=80, blank=True)
    fecha_ingreso = models.DateTimeField(null=True, blank=True)
    fecha_retiro = models.DateTimeField(null=True, blank=True)
    horario_trabajo = models.CharField(max_length=120, blank=True)
    jornada_vs = models.CharField(max_length=8, blank=True)
    jornada_contrato = models.CharField(max_length=8, blank=True)

    class Meta:
        db_table = "data_employee"
        ordering = ["nombre", "codigo_ficha"]
        verbose_name = "Trabajador"
        verbose_name_plural = "Trabajadores"
        permissions = [
            ("access_payroll_module", "Puede acceder al modulo de remuneraciones"),
            ("manage_employee_status", "Puede cambiar estados de trabajadores"),
        ]

    def __str__(self) -> str:
        return f"{self.codigo_ficha} - {self.nombre}"


class PayrollPeriod(TimeStampedModel):
    periodo = models.CharField(max_length=6, unique=True)
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "data_payroll_period"
        ordering = ["periodo"]
        verbose_name = "Periodo"
        verbose_name_plural = "Periodos"

    def __str__(self) -> str:
        return self.periodo


class PayrollItem(TimeStampedModel):
    CATEGORY_ASIGNACIONES = "asignaciones_familiares"
    CATEGORY_CONTRIBUCION = "contribucion_empleador"
    CATEGORY_DESCUENTOS_LEGALES = "descuentos_legales_previsionales"
    CATEGORY_HABERES_EXENTOS = "haberes_exentos_no_imponibles"
    CATEGORY_HABERES_IMPONIBLES = "haberes_normales_imponibles"
    CATEGORY_OTROS_DESCUENTOS = "otros_descuentos"
    CATEGORY_PROVISIONES = "provisiones"
    CATEGORY_TOTALES = "totales"

    CATEGORY_CHOICES = [
        (CATEGORY_ASIGNACIONES, "Asignaciones familiares"),
        (CATEGORY_CONTRIBUCION, "Contribucion empleador"),
        (CATEGORY_DESCUENTOS_LEGALES, "Descuentos legales previsionales"),
        (CATEGORY_HABERES_EXENTOS, "Haberes exentos no imponibles"),
        (CATEGORY_HABERES_IMPONIBLES, "Haberes normales imponibles"),
        (CATEGORY_OTROS_DESCUENTOS, "Otros descuentos"),
        (CATEGORY_PROVISIONES, "Provisiones"),
        (CATEGORY_TOTALES, "Totales"),
    ]

    codigo = models.CharField(max_length=32, unique=True)
    categoria = models.CharField(max_length=80, choices=CATEGORY_CHOICES)
    descripcion = models.CharField(max_length=255, blank=True)
    requiere_confirmacion = models.BooleanField(default=False)

    class Meta:
        db_table = "data_payroll_item"
        ordering = ["categoria", "codigo"]
        verbose_name = "Item de remuneracion"
        verbose_name_plural = "Items de remuneracion"

    def __str__(self) -> str:
        label = self.descripcion or self.codigo
        return f"{self.codigo} - {label}"


class PayrollEntry(TimeStampedModel):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="payroll_entries")
    period = models.ForeignKey(PayrollPeriod, on_delete=models.PROTECT, related_name="payroll_entries")
    item = models.ForeignKey(PayrollItem, on_delete=models.PROTECT, related_name="payroll_entries")
    monto = models.DecimalField(max_digits=16, decimal_places=0)

    class Meta:
        db_table = "data_payroll_entry"
        ordering = ["period__periodo", "employee__codigo_ficha", "item__categoria", "item__codigo"]
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"
        indexes = [
            models.Index(fields=["period", "employee"]),
            models.Index(fields=["item"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "period", "item"],
                name="unique_payroll_entry_employee_period_item",
            )
        ]

    def __str__(self) -> str:
        return f"{self.period} {self.employee.codigo_ficha} {self.item.codigo}: {self.monto}"


class PayrollSummary(TimeStampedModel):
    document_number = models.CharField(max_length=80, unique=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="payroll_summaries")
    period = models.ForeignKey(PayrollPeriod, on_delete=models.PROTECT, related_name="payroll_summaries")
    rut_empresa = models.CharField(max_length=32, blank=True)

    sueldo_base = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    dias_laborales = models.PositiveSmallIntegerField(default=0)
    dias_trabajados = models.PositiveSmallIntegerField(default=0)
    dias_licencias = models.PositiveSmallIntegerField(default=0)
    dias_permisos = models.PositiveSmallIntegerField(default=0)
    dias_ausencias = models.PositiveSmallIntegerField(default=0)
    dias_suspendidos = models.PositiveSmallIntegerField(default=0)
    horas_no_trabajadas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    horas_extras = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    costo_empresa = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    total_haberes_imponibles = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    total_haberes_no_imponibles = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    total_haberes_no_imponibles_tributables = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    total_descuentos_legales = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    total_otros_descuentos = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    sueldo_liquido = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    base_tributable = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    impuesto = models.DecimalField(max_digits=16, decimal_places=0, default=0)

    pago_prevision = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    pago_salud_obligatoria = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    pago_salud_voluntaria = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    pago_prevision_voluntaria = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    seguro_cesantia_trabajador = models.DecimalField(max_digits=16, decimal_places=0, default=0)

    seguro_cesantia_empleador = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    mutual_empleador = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    pago_sis_empleador = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    afp_prevision_empleador = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    ley_sanna = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    otros_aportes_patronales = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    saldo_sobregiro = models.DecimalField(max_digits=16, decimal_places=0, default=0)

    class Meta:
        db_table = "data_payroll_summary"
        ordering = ["period__periodo", "employee__codigo_ficha"]
        verbose_name = "Liquidacion"
        verbose_name_plural = "Liquidaciones"
        indexes = [
            models.Index(fields=["period", "employee"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "period"],
                name="unique_payroll_summary_employee_period",
            )
        ]

    def __str__(self) -> str:
        return self.document_number


class ImportRun(TimeStampedModel):
    STATUS_STARTED = "started"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_STARTED, "Iniciada"),
        (STATUS_SUCCESS, "Exitosa"),
        (STATUS_FAILED, "Fallida"),
    ]

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_STARTED)
    transformed_path = models.CharField(max_length=500)
    summaries_path = models.CharField(max_length=500)
    descriptions_dir = models.CharField(max_length=500, blank=True)
    transformed_sha256 = models.CharField(max_length=64, blank=True)
    summaries_sha256 = models.CharField(max_length=64, blank=True)
    clear_requested = models.BooleanField(default=False)
    employee_count = models.PositiveIntegerField(default=0)
    period_count = models.PositiveIntegerField(default=0)
    item_count = models.PositiveIntegerField(default=0)
    entry_count = models.PositiveIntegerField(default=0)
    summary_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "data_import_run"
        ordering = ["-created_at"]
        verbose_name = "Carga ETL"
        verbose_name_plural = "Cargas ETL"
        permissions = [
            ("upload_payroll_data", "Puede cargar archivos de remuneraciones"),
            ("import_payroll_data", "Puede importar datos al ERP"),
            ("clear_payroll_data", "Puede limpiar datos antes de importar"),
            ("download_upload_output", "Puede descargar salidas de cargas ETL"),
        ]

    def __str__(self) -> str:
        return f"{self.created_at:%Y-%m-%d %H:%M:%S} - {self.status}"
