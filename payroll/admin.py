from django.contrib import admin

from .models import PayrollConfig, PayrollRun, Payslip


@admin.register(PayrollConfig)
class PayrollConfigAdmin(admin.ModelAdmin):
    list_display = (
        "pay_day",
        "overtime_threshold",
        "overtime_multiplier",
        "tax_year",
        "pay_frequency",
    )
    name = "Payroll configuration"


@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = (
        "period",
        "status",
        "payslip_count",
        "gross_total",
        "deductions_total",
        "net_total",
        "employer_nic_total",
        "generated_at",
    )
    list_filter = ("status",)


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = (
        "pay_reference",
        "period",
        "employee",
        "gross_amount",
        "tax_amount",
        "ni_amount",
        "net_amount",
        "status",
    )
    list_filter = ("status", "period")
    search_fields = ("pay_reference", "employee__full_name")
