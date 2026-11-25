from django import forms
from django.forms import DateInput, ModelForm, inlineformset_factory

from .models import Certification, Employee


class EmployeeForm(forms.ModelForm):
    placeholders = {
        "full_name": "e.g. Maria Gonzalez",
        "email": "maria@cleaners.co.uk",
        "phone": "07700 900123",
        "address": "12 High Street, London",
        "ni_number": "AB123456C",
        "tax_code": "1257L",
        "bank_sort_code": "04-00-04",
        "bank_account_number": "12345678",
        "hourly_rate": "12.50",
        "right_to_work_document_ref": "Passport/share code ref (no full copy stored)",
        "dbs_certificate_number": "DBS certificate number",
        "emergency_contact_name": "Emergency contact name",
        "emergency_contact_phone": "Emergency contact phone",
    }

    class Meta:
        model = Employee
        fields = (
            "full_name", "email", "phone", "address", "job_role", "hourly_rate", "salary_monthly", "is_cis",
            "employment_status", "start_date", "ni_number", "tax_code", "bank_sort_code", "bank_account_number",
            "right_to_work_status", "right_to_work_check_date", "right_to_work_expiry_date", "right_to_work_document_ref", "right_to_work_notes",
            "dbs_status", "dbs_certificate_number", "dbs_issue_date", "dbs_expiry_date", "dbs_notes",
            "induction_completed_date", "health_safety_training_date", "coshh_training_date", "risk_assessment_ack_date", "ppe_provided_date",
            "emergency_contact_name", "emergency_contact_phone",
        )
        widgets = {
            "start_date": DateInput(attrs={"type": "date"}),
            "hourly_rate": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "salary_monthly": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "employment_status": forms.Select(),
            "job_role": forms.Select(),
            "right_to_work_status": forms.Select(),
            "right_to_work_check_date": DateInput(attrs={"type": "date"}),
            "right_to_work_expiry_date": DateInput(attrs={"type": "date"}),
            "right_to_work_notes": forms.Textarea(attrs={"rows": 2}),
            "dbs_status": forms.Select(),
            "dbs_issue_date": DateInput(attrs={"type": "date"}),
            "dbs_expiry_date": DateInput(attrs={"type": "date"}),
            "dbs_notes": forms.Textarea(attrs={"rows": 2}),
            "induction_completed_date": DateInput(attrs={"type": "date"}),
            "health_safety_training_date": DateInput(attrs={"type": "date"}),
            "coshh_training_date": DateInput(attrs={"type": "date"}),
            "risk_assessment_ack_date": DateInput(attrs={"type": "date"}),
            "ppe_provided_date": DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.placeholders:
                field.widget.attrs.setdefault("placeholder", self.placeholders[name])


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = (
            "name",
            "certification_type",
            "issuing_body",
            "credential_id",
            "issue_date",
            "expiry_date",
        )
        widgets = {
            "issue_date": DateInput(attrs={"type": "date"}),
            "expiry_date": DateInput(attrs={"type": "date"}),
        }


from django.forms import inlineformset_factory  # noqa: E402

EmployeeCertFormSet = inlineformset_factory(
    Employee,
    Certification,
    form=CertificationForm,
    fields=(
        "name",
        "certification_type",
        "issuing_body",
        "credential_id",
        "issue_date",
        "expiry_date",
    ),
    extra=0,
    can_delete=False,
    max_num=10,
)
