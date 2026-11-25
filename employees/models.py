"""Cleaning staff: employees, roles and certifications."""

from datetime import date

from django.conf import settings
from django.db import models
from decimal import Decimal


class Employee(models.Model):
    """A person working for the cleaning company (PAYE employee)."""

    JOB_ROLE_CHOICES = (
        ("cleaner", "Cleaner"),
        ("senior_cleaner", "Senior Cleaner"),
        ("team_leader", "Team Leader"),
        ("supervisor", "Supervisor"),
        ("manager", "Manager"),
    )

    EMPLOYMENT_STATUS_CHOICES = (
        ("active", "Active"),
        ("on_leave", "On Leave"),
        ("terminated", "Terminated"),
    )

    RTW_STATUS_CHOICES = (
        ("not_checked", "Not checked"),
        ("checked", "Checked - evidence retained"),
        ("follow_up", "Follow-up required"),
        ("expired", "Expired / time-limited"),
    )

    DBS_STATUS_CHOICES = (
        ("not_required", "Not required"),
        ("required", "Required"),
        ("applied", "Applied"),
        ("clear", "Clear / received"),
        ("expired", "Expired / renewal due"),
    )

    CERTIFICATION_TYPE_CHOICES = (
        ("cossh", "COSHH"),
        ("dbs", "DBS Check"),
        ("first_aid", "First Aid"),
        ("fire_safety", "Fire Safety"),
        ("manual_handling", "Manual Handling"),
        ("health_safety", "Health & Safety"),
        ("food_safety", "Food Safety"),
        ("other", "Other"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")
    address = models.CharField(max_length=255, blank=True, default="")
    job_role = models.CharField(max_length=40, choices=JOB_ROLE_CHOICES, default="cleaner")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("12.50"))
    salary_monthly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=None)
    is_cis = models.BooleanField(default=False)
    employment_status = models.CharField(
        max_length=12, choices=EMPLOYMENT_STATUS_CHOICES, default="active"
    )
    start_date = models.DateField(default=date.today)
    ni_number = models.CharField(max_length=20, blank=True, default="")
    tax_code = models.CharField(max_length=20, blank=True, default="")
    bank_sort_code = models.CharField(max_length=12, blank=True, default="")
    bank_account_number = models.CharField(max_length=12, blank=True, default="")

    # UK right-to-work / identity checks (Home Office prevention of illegal working)
    right_to_work_status = models.CharField(max_length=20, choices=RTW_STATUS_CHOICES, default="not_checked")
    right_to_work_check_date = models.DateField(null=True, blank=True)
    right_to_work_expiry_date = models.DateField(null=True, blank=True)
    right_to_work_document_ref = models.CharField(max_length=120, blank=True, default="", help_text="Reference only; avoid storing unnecessary document copies.")
    right_to_work_notes = models.TextField(blank=True, default="")

    # DBS checks (only where role/client/site requires it)
    dbs_status = models.CharField(max_length=20, choices=DBS_STATUS_CHOICES, default="not_required")
    dbs_certificate_number = models.CharField(max_length=80, blank=True, default="")
    dbs_issue_date = models.DateField(null=True, blank=True)
    dbs_expiry_date = models.DateField(null=True, blank=True)
    dbs_notes = models.TextField(blank=True, default="")

    # Health & safety / training records
    induction_completed_date = models.DateField(null=True, blank=True)
    health_safety_training_date = models.DateField(null=True, blank=True)
    coshh_training_date = models.DateField(null=True, blank=True)
    risk_assessment_ack_date = models.DateField(null=True, blank=True)
    ppe_provided_date = models.DateField(null=True, blank=True)

    emergency_contact_name = models.CharField(max_length=120, blank=True, default="")
    emergency_contact_phone = models.CharField(max_length=30, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name

    @property
    def right_to_work_ok(self):
        if self.right_to_work_status != "checked":
            return False
        return not (self.right_to_work_expiry_date and self.right_to_work_expiry_date < date.today())

    @property
    def dbs_ok(self):
        if self.dbs_status in {"not_required", "clear"}:
            if self.dbs_status == "clear" and self.dbs_expiry_date and self.dbs_expiry_date < date.today():
                return False
            return True
        return False

    @property
    def has_health_safety_basics(self):
        return bool(self.induction_completed_date and self.health_safety_training_date)

    @property
    def compliance_warnings(self):
        warnings = []
        if not self.right_to_work_ok:
            warnings.append("Right to work check missing/expired")
        if not self.dbs_ok:
            warnings.append("DBS required or expired")
        if not self.has_health_safety_basics:
            warnings.append("H&S induction/training incomplete")
        if self.right_to_work_expiry_date and self.right_to_work_expiry_date < date.today():
            warnings.append("Right to work expired")
        if self.dbs_expiry_date and self.dbs_expiry_date < date.today():
            warnings.append("DBS expired")
        return warnings


class Certification(models.Model):
    """A safety / compliance certificate attached to an employee."""

    CERTIFICATION_TYPE_CHOICES = (
        ("cossh", "COSHH"),
        ("dbs", "DBS Check"),
        ("first_aid", "First Aid"),
        ("fire_safety", "Fire Safety"),
        ("manual_handling", "Manual Handling"),
        ("health_safety", "Health & Safety"),
        ("food_safety", "Food Safety"),
        ("other", "Other"),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=140)
    certification_type = models.CharField(max_length=20, choices=CERTIFICATION_TYPE_CHOICES, default="other")
    issuing_body = models.CharField(max_length=120, blank=True, default="")
    credential_id = models.CharField(max_length=80, blank=True, default="")
    issue_date = models.DateField()
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-expiry_date", "name"]

    def __str__(self):
        return f"{self.name} ({self.employee.full_name})"

    @property
    def is_valid(self):
        """A certificate is valid while it has not expired."""
        return bool(self.expiry_date) and self.expiry_date >= date.today()
