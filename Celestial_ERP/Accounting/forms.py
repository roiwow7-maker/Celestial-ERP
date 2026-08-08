from __future__ import annotations

from django import forms

from .models import ChartAccount, CostCenter, PayrollItemAccountMapping


class BaseAccountingForm(forms.ModelForm):
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


class ChartAccountForm(BaseAccountingForm):
    class Meta:
        model = ChartAccount
        fields = ["code", "name", "account_type", "parent", "is_active"]


class CostCenterForm(BaseAccountingForm):
    class Meta:
        model = CostCenter
        fields = ["code", "name", "description", "is_active"]


class PayrollItemAccountMappingForm(BaseAccountingForm):
    class Meta:
        model = PayrollItemAccountMapping
        fields = ["payroll_item", "account", "movement_type", "cost_center", "is_active"]


class GeneratePayrollJournalForm(forms.Form):
    period = forms.ModelChoiceField(label="Periodo", queryset=None)
    replace_existing = forms.BooleanField(label="Reemplazar asiento existente del periodo", required=False)

    def __init__(self, *args, **kwargs):
        from DATA_scope.models import PayrollPeriod

        super().__init__(*args, **kwargs)
        self.fields["period"].queryset = PayrollPeriod.objects.order_by("-periodo")
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"
