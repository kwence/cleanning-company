from django import forms
from django.forms import ModelForm

from .models import Shift


class ShiftForm(forms.ModelForm):
    placeholders = {
        "notes": "e.g. Ground floor only, access via rear door",
    }

    class Meta:
        model = Shift
        fields = ("employee", "client", "date", "start_time", "end_time", "status", "notes")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "notes" in self.fields:
            self.fields["notes"].widget.attrs.setdefault("placeholder", "Access codes, parking notes...")
