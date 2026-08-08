from __future__ import annotations

from django import forms

from .models import Product, StockMovement, Warehouse


class BaseInventoryForm(forms.ModelForm):
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


class ProductForm(BaseInventoryForm):
    class Meta:
        model = Product
        fields = ["sku", "name", "category", "unit", "description", "minimum_stock", "standard_cost", "is_active"]


class WarehouseForm(BaseInventoryForm):
    class Meta:
        model = Warehouse
        fields = ["code", "name", "location", "is_active"]


class StockMovementForm(BaseInventoryForm):
    class Meta:
        model = StockMovement
        fields = ["product", "warehouse", "movement_type", "date", "quantity", "unit_cost", "reference", "note"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
