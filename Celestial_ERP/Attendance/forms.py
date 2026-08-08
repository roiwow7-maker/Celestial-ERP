from __future__ import annotations

from django import forms

from .models import AttendanceRecord


class BaseAttendanceForm(forms.ModelForm):
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


class AttendanceRecordForm(BaseAttendanceForm):
    class Meta:
        model = AttendanceRecord
        fields = ["employee", "date", "check_in", "check_out", "break_minutes", "status", "source", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "check_in": forms.TimeInput(attrs={"type": "time"}),
            "check_out": forms.TimeInput(attrs={"type": "time"}),
        }
