from django import forms
from django.forms import ModelForm

from .models import TimeEntry


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ("employee", "shift", "date", "clock_in", "clock_out", "notes")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "clock_in": forms.TimeInput(attrs={"type": "time"}),
            "clock_out": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
