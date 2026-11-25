"""Payroll: UK PAYE runs, payslips and wage payments."""

from django.db import models


class PayrollConfig(models.Model):
    """Company-wide payroll settings (single record)."""

    pay_day = models.PositiveSmallIntegerField(default=28)
    overtime_threshold = models.PositiveIntegerField(default=40)
    overtime_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.5)
    tax_year = models.PositiveSmallIntegerField(default=2025)
    pay_frequency = models.CharField(max_length=12, choices=(("monthly", "Monthly"),), default="monthly")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payroll configuration"

    def __str__(self):
        return f"Payroll config · tax year {self.tax_year} · OT > {self.overtime_threshold}h"


class PayrollRun(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("issued", "Issued"),
        ("paid", "Paid"),
    )

    period = models.CharField(max_length=7, unique=True, help_text="Pay period in YYYY-MM format.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    generated_at = models.DateTimeField(null=True, blank=True)
    gross_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    deductions_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    employer_nic_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    payslip_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-period"]

    def __str__(self):
        return f"Payroll {self.period} · {self.get_status_display()}"


class Payslip(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("issued", "Issued"),
        ("emailed", "Emailed"),
        ("paid", "Paid"),
    )

    run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name="payslips")
    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.PROTECT, related_name="payslips"
    )
    period = models.CharField(max_length=7)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ni_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    employer_nic = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cis_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pay_reference = models.CharField(max_length=40)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    issued_at = models.DateTimeField(null=True, blank=True)
    emailed_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-run", "employee__full_name"]

    def __str__(self):
        return f"{self.pay_reference} · {self.employee.full_name} · {self.net_amount}"

    @property
    def period_label(self):
        year, month = (int(part) for part in str(self.period).split("-"))
        return f"{year}-{month:02d}"
