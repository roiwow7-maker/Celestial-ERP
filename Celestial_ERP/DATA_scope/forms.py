from __future__ import annotations

from django import forms

from .models import Employee, PayrollEntry, PayrollItem, PayrollPeriod, PayrollSummary


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"


class BaseStyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            if isinstance(field.widget, forms.CheckboxInput):
                bootstrap_class = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                bootstrap_class = "form-select"
            else:
                bootstrap_class = "form-control"
            field.widget.attrs["class"] = f"{css_class} {bootstrap_class}".strip()


class EmployeeForm(BaseStyledModelForm):
    class Meta:
        model = Employee
        fields = [
            "codigo_ficha",
            "rut",
            "nombre",
            "estado",
            "division",
            "afp",
            "isapre",
            "fecha_ingreso",
            "fecha_retiro",
            "horario_trabajo",
            "jornada_vs",
            "jornada_contrato",
        ]
        widgets = {
            "fecha_ingreso": DateTimeLocalInput(format="%Y-%m-%dT%H:%M"),
            "fecha_retiro": DateTimeLocalInput(format="%Y-%m-%dT%H:%M"),
        }


class PayrollPeriodForm(BaseStyledModelForm):
    class Meta:
        model = PayrollPeriod
        fields = ["periodo", "year", "month"]

    def clean_periodo(self):
        periodo = self.cleaned_data["periodo"].strip()
        if len(periodo) != 6 or not periodo.isdigit():
            raise forms.ValidationError("Usa formato AAAAMM, por ejemplo 202606.")
        return periodo

    def clean(self):
        cleaned = super().clean()
        periodo = cleaned.get("periodo")
        year = cleaned.get("year")
        month = cleaned.get("month")
        if periodo and year and month:
            if int(periodo[:4]) != year or int(periodo[4:]) != month:
                raise forms.ValidationError("El periodo debe coincidir con ano y mes.")
        return cleaned


class PayrollItemForm(BaseStyledModelForm):
    class Meta:
        model = PayrollItem
        fields = ["codigo", "categoria", "descripcion", "requiere_confirmacion"]


class PayrollSummaryForm(BaseStyledModelForm):
    class Meta:
        model = PayrollSummary
        fields = [
            "document_number",
            "employee",
            "period",
            "rut_empresa",
            "sueldo_base",
            "dias_laborales",
            "dias_trabajados",
            "dias_licencias",
            "dias_permisos",
            "dias_ausencias",
            "dias_suspendidos",
            "horas_no_trabajadas",
            "horas_extras",
            "costo_empresa",
            "total_haberes_imponibles",
            "total_haberes_no_imponibles",
            "total_haberes_no_imponibles_tributables",
            "total_descuentos_legales",
            "total_otros_descuentos",
            "sueldo_liquido",
            "base_tributable",
            "impuesto",
            "pago_prevision",
            "pago_salud_obligatoria",
            "pago_salud_voluntaria",
            "pago_prevision_voluntaria",
            "seguro_cesantia_trabajador",
            "seguro_cesantia_empleador",
            "mutual_empleador",
            "pago_sis_empleador",
            "afp_prevision_empleador",
            "ley_sanna",
            "otros_aportes_patronales",
            "saldo_sobregiro",
        ]


class PayrollEntryForm(BaseStyledModelForm):
    class Meta:
        model = PayrollEntry
        fields = ["employee", "period", "item", "monto"]
