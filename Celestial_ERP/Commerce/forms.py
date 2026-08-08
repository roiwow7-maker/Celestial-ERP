from __future__ import annotations

from django import forms

from .models import Customer, PurchaseOrder, PurchaseOrderLine, SalesOrder, SalesOrderLine, Supplier


class BaseCommerceForm(forms.ModelForm):
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


class SupplierForm(BaseCommerceForm):
    class Meta:
        model = Supplier
        fields = ["code", "name", "tax_id", "email", "phone", "address", "is_active"]


class CustomerForm(BaseCommerceForm):
    class Meta:
        model = Customer
        fields = ["code", "name", "tax_id", "email", "phone", "address", "is_active"]


class PurchaseOrderForm(BaseCommerceForm):
    class Meta:
        model = PurchaseOrder
        fields = ["number", "supplier", "date", "expected_date", "status", "notes"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"}), "expected_date": forms.DateInput(attrs={"type": "date"})}


class PurchaseOrderLineForm(BaseCommerceForm):
    class Meta:
        model = PurchaseOrderLine
        fields = ["product", "description", "quantity", "unit_cost"]


class SalesOrderForm(BaseCommerceForm):
    class Meta:
        model = SalesOrder
        fields = ["number", "customer", "date", "due_date", "status", "notes"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"}), "due_date": forms.DateInput(attrs={"type": "date"})}


class SalesOrderLineForm(BaseCommerceForm):
    class Meta:
        model = SalesOrderLine
        fields = ["product", "description", "quantity", "unit_price"]
