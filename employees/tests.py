"""Tests for employee and certification management."""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Certification, Employee

User = get_user_model()


class EmployeeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="StrongPass123!")

    def test_employee_list_shows_employees(self):
        Employee.objects.create(full_name="Maria Gonzalez", hourly_rate=12.5, start_date=date.today(), employment_status="active")
        self.client.force_login(self.user)
        response = self.client.get(reverse("employee_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maria Gonzalez")

    def test_employee_create(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("employee_create"), {
            "full_name": "John Smith",
            "email": "john@cleansweep.co.uk",
            "phone": "07700 900999",
            "address": "1 Test Road, London",
            "job_role": "cleaner",
            "hourly_rate": "12.50",
            "employment_status": "active",
            "start_date": date.today().isoformat(),
            "ni_number": "AB999999Z",
            "tax_code": "1257L",
            "bank_sort_code": "04-00-04",
            "bank_account_number": "12345678",
            "right_to_work_status": "checked",
            "right_to_work_check_date": date.today().isoformat(),
            "dbs_status": "not_required",
        })
        self.assertRedirects(response, reverse("employee_list"))
        self.assertTrue(Employee.objects.filter(full_name="John Smith").exists())

    def test_certification_linked_to_employee(self):
        employee = Employee.objects.create(full_name="Jane Cleaner", hourly_rate=12, start_date=date.today(), employment_status="active")
        cert = Certification.objects.create(
            employee=employee, name="COSHH Awareness", certification_type="cossh",
            issue_date=date.today(), expiry_date=date.today().replace(year=date.today().year + 1),
        )
        self.assertTrue(cert.is_valid)
        employee.refresh_from_db()
        self.assertEqual(employee.certifications.count(), 1)
