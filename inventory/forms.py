from django import forms

from .models import Equipment, StockItem, StockMovement, StockOrder


class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = [
            "name", "category", "sku", "unit", "supplier", "location", "minimum_stock", "reorder_quantity",
            "coshh_required", "sds_url", "hazard_notes", "ppe_notes", "storage_notes", "is_active",
        ]
        widgets = {
            "hazard_notes": forms.Textarea(attrs={"rows": 2}),
            "ppe_notes": forms.Textarea(attrs={"rows": 2}),
            "storage_notes": forms.Textarea(attrs={"rows": 2}),
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ["item", "movement_type", "quantity", "movement_date", "reference", "notes"]
        widgets = {
            "movement_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty == 0:
            raise forms.ValidationError("Quantity cannot be zero.")
        movement_type = self.cleaned_data.get("movement_type")
        if movement_type == "out":
            return -abs(qty)
        if movement_type == "in":
            return abs(qty)
        return qty


class StockOrderForm(forms.ModelForm):
    class Meta:
        model = StockOrder
        fields = ["item", "supplier", "quantity", "unit_cost", "order_date", "expected_date", "received_date", "status", "reference", "notes"]
        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "expected_date": forms.DateInput(attrs={"type": "date"}),
            "received_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get("status")
        received_date = cleaned.get("received_date")
        if status == "received" and not received_date:
            cleaned["received_date"] = forms.fields.DateField().to_python(
                self.data.get("received_date")
            ) or None
        return cleaned


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            "name", "equipment_type", "asset_tag", "serial_number", "location", "assigned_to", "status",
            "purchase_date", "last_service_date", "next_service_date", "pat_test_date", "pat_due_date",
            "risk_assessment_date", "puwer_inspection_date", "is_safe_to_use", "notes",
        ]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "last_service_date": forms.DateInput(attrs={"type": "date"}),
            "next_service_date": forms.DateInput(attrs={"type": "date"}),
            "pat_test_date": forms.DateInput(attrs={"type": "date"}),
            "pat_due_date": forms.DateInput(attrs={"type": "date"}),
            "risk_assessment_date": forms.DateInput(attrs={"type": "date"}),
            "puwer_inspection_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        is_safe = cleaned.get("is_safe_to_use")
        status = cleaned.get("status")
        if not is_safe and status == "available":
            cleaned["status"] = "quarantine"
        return cleaned
