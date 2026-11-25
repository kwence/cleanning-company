from django.contrib import admin

from .models import Certification, Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "job_role", "hourly_rate", "employment_status", "start_date", "ni_number")
    list_filter = ("employment_status", "job_role")
    search_fields = ("full_name", "email", "ni_number", "tax_code")


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("name", "employee", "certification_type", "issue_date", "expiry_date", "is_valid")
    list_filter = ("certification_type",)
    search_fields = ("name", "credential_id", "employee__full_name")
