from django.urls import path

from . import views

urlpatterns = [
    path("", views.payroll_home, name="payroll_home"),
    path("generate/", views.payroll_generate, name="payroll_generate"),
    path(
        "employee/<int:employee_pk>/generate/",
        views.payroll_generate_employee,
        name="payroll_generate_employee",
    ),
    path("config/", views.payroll_config_view, name="payroll_config"),
    path("<int:pk>/", views.payroll_payslip, name="payslip"),
    path("<int:pk>/email/", views.payroll_payslip_email, name="payslip_email"),
    path("<int:pk>/paid/", views.payroll_mark_paid, name="payslip_paid"),
]
