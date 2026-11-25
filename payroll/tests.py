"""Tests for UK payroll calculations, generation and payslip emailing."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from accounting.models import Payment
from employees.models import Employee
from payroll.models import PayrollRun, Payslip
from payroll.services import (
    calculate_employee_pay,
    employee_ni,
    employer_nic,
    generate_payroll,
    income_tax,
    period_bounds,
)
from timeclock.models import TimeEntry

User = get_user_model()


class UkTaxTests(TestCase):
    def test_income_tax_uses_personal_allowance(self):
        self.assertEqual(income_tax(Decimal("12570"), 2025), Decimal("0"))
        self.assertEqual(income_tax(Decimal("60000"), 2025), Decimal("11432"))
        self.assertEqual(income_tax(Decimal("140000"), 2025), Decimal("44175.00"))

    def test_employee_ni_2025(self):
        self.assertEqual(employee_ni(Decimal("10000"), 2025), Decimal("0"))
        self.assertEqual(employee_ni(Decimal("60000"), 2025), Decimal("3210.60"))
        self.assertEqual(employer_nic(Decimal("200000"), 2025), Decimal("27600.00"))

    def test_period_bounds(self):
        start, end = period_bounds("2026-02")
        self.assertEqual(start, date(2026, 2, 1))
        self.assertEqual(end, date(2026, 2, 28))


class PayrollGenerationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="StrongPass123!")
        self.employee = Employee.objects.create(
            full_name="Maria Gonzalez", hourly_rate=Decimal("12.50"), start_date=date.today(), employment_status="active",
        )

    def test_generate_payroll_creates_payslip_from_approved_hours(self):
        TimeEntry.objects.create(
            employee=self.employee, date=date.today(), clock_in="09:00", clock_out="13:00", approved=True, approved_by=self.user,
        )
        run = generate_payroll(f"{date.today().year:04d}-{date.today().month:02d}")[0]
        self.assertEqual(run.payslip_count, 1)
        payslip = run.payslips.get(employee=self.employee)
        # 4 hours at £12.50 = £50 gross, no tax or NI due to personal allowance.
        self.assertEqual(payslip.gross_amount, Decimal("50.00"))
        self.assertEqual(payslip.net_amount, Decimal("50.00"))
        self.assertEqual(payslip.tax_amount, Decimal("0.00"))
        self.assertEqual(payslip.ni_amount, Decimal("0.00"))
        self.assertEqual(payslip.status, "draft")

    def test_payslip_email_flow_marks_emailed(self):
        from payroll.services import issue_and_email_run

        TimeEntry.objects.create(
            employee=self.employee, date=date.today(), clock_in="09:00", clock_out="13:00", approved=True, approved_by=self.user,
        )
        self.employee.email = "maria@cleansweep.co.uk"
        self.employee.save(update_fields=["email"])
        run = generate_payroll(f"{date.today().year:04d}-{date.today().month:02d}")[0]
        results, sent_count, failed_count = issue_and_email_run(run)
        self.assertEqual(len(results), 1)
        self.assertEqual(sent_count, 1)
        self.assertEqual(failed_count, 0)
        self.assertEqual(results[0]["payslip"].status, "emailed")
        self.assertTrue(results[0]["payslip"].emailed_at is not None)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("payslip", mail.outbox[0].subject.lower())

    def test_mark_paid_creates_accounting_payment(self):
        TimeEntry.objects.create(
            employee=self.employee, date=date.today(), clock_in="09:00", clock_out="13:00", approved=True, approved_by=self.user,
        )
        run = generate_payroll(f"{date.today().year:04d}-{date.today().month:02d}")[0]
        payslip = run.payslips.get(employee=self.employee)
        payslip.status = "paid"
        payslip.save(update_fields=["status"])
        from django.utils import timezone

        Payment.objects.get_or_create(
            payslip=payslip,
            defaults={
                "employee": payslip.employee,
                "amount": payslip.net_amount,
                "payment_date": date.today(),
                "method": "bank_transfer",
                "status": "paid",
                "transaction_ref": f"W-{payslip.pay_reference}",
                "paid_at": timezone.now(),
            },
        )
        self.assertTrue(Payment.objects.filter(payslip=payslip, status="paid").exists())


class SalaryAndCISPayrollTests(TestCase):
    def test_salaried_employee_gets_monthly_gross_without_hours(self):
        Employee.objects.create(
            full_name="Salaried Manager", hourly_rate=Decimal("18"), salary_monthly=Decimal("1800"),
            start_date=date.today(), employment_status="active",
        )
        run = generate_payroll(f"{date.today().year:04d}-{date.today().month:02d}")[0]
        self.assertEqual(run.payslip_count, 1)
        payslip = run.payslips.get(employee__full_name="Salaried Manager")
        self.assertEqual(payslip.gross_amount, Decimal("1800.00"))
        self.assertEqual(payslip.net_amount, Decimal("1800.00"))

    def test_cis_subcontractor_gets_net_after_cis_deduction(self):
        Employee.objects.create(
            full_name="Subcontractor Helper", hourly_rate=Decimal("12"), salary_monthly=Decimal("1500"),
            is_cis=True, start_date=date.today(), employment_status="active",
        )
        run = generate_payroll(f"{date.today().year:04d}-{date.today().month:02d}")[0]
        payslip = run.payslips.get(employee__full_name="Subcontractor Helper")
        self.assertEqual(payslip.gross_amount, Decimal("1500.00"))
        self.assertEqual(payslip.cis_amount, Decimal("300.00"))
        self.assertEqual(payslip.net_amount, Decimal("1200.00"))
        self.assertEqual(payslip.tax_amount, Decimal("0.00"))


class PayrollViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="StrongPass123!")
        self.employee = Employee.objects.create(
            full_name="Maria Gonzalez", hourly_rate=Decimal("12.50"), start_date=date.today(), employment_status="active",
        )

    def test_payroll_home_requires_login(self):
        response = self.client.get(reverse("payroll_home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_generate_payroll_via_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("payroll_generate"), {"period": f"{date.today().year:04d}-{date.today().month:02d}"})
        self.assertRedirects(response, reverse("payroll_home"))
        self.assertTrue(PayrollRun.objects.filter(period=f"{date.today().year:04d}-{date.today().month:02d}").exists())

    def test_generate_single_employee_payslip(self):
        self.client.force_login(self.user)
        period = f"{date.today().year:04d}-{date.today().month:02d}"
        TimeEntry.objects.create(
            employee=self.employee, date=date.today(), clock_in="09:00", clock_out="13:00", approved=True, approved_by=self.user,
        )
        response = self.client.post(
            reverse("payroll_generate_employee", args=[self.employee.pk]),
            {"period": period},
        )
        payslip = Payslip.objects.get(employee=self.employee, period=period)
        self.assertRedirects(response, reverse("payslip", args=[payslip.pk]))
        self.assertEqual(payslip.gross_amount, Decimal("50.00"))

    def test_payslip_print_view(self):
        self.client.force_login(self.user)
        period = f"{date.today().year:04d}-{date.today().month:02d}"
        TimeEntry.objects.create(
            employee=self.employee, date=date.today(), clock_in="09:00", clock_out="13:00", approved=True, approved_by=self.user,
        )
        run = generate_payroll(period)[0]
        payslip = run.payslips.get(employee=self.employee)
        response = self.client.get(reverse("payslip", args=[payslip.pk]) + "?print=1")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "window.print()")
