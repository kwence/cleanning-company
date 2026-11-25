from django import forms
from django.forms import ModelForm

from .models import Client


class ClientForm(forms.ModelForm):
    placeholders = {
        "name": "e.g. Riverside Care Home",
        "contact_name": "e.g. Jane Smith",
        "email": "admin@riversidecare.org",
        "phone": "01234 567890",
        "address": "12 High Street, London",
        "notes": "Access codes, key holders, parking notes...",
    }

    class Meta:
        model = Client
        fields = (
            "name",
            "contact_name",
            "email",
            "phone",
            "address",
            "notes",
            "status",
        )
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "status": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.placeholders:
                field.widget.attrs.setdefault("placeholder", self.placeholders[name])
