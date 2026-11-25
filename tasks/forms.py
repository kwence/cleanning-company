from django import forms
from django.forms import ModelForm

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "client",
            "employee",
            "shift",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
