"""Tests for shift scheduling."""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clients.models import Client
from employees.models import Employee
from .models import Shift

User = get_user_model()


class ShiftViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="StrongPass123!")
        self.employee = Employee.objects.create(full_name="Maria Gonzalez", hourly_rate=12.5, start_date=date.today(), employment_status="active")
        self.client_obj = Client.objects.create(name="Riverside Care Home", status="active")

    def test_shift_create_and_complete(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("shift_create"), {
            "employee": self.employee.pk,
            "client": self.client_obj.pk,
            "date": date.today().isoformat(),
            "start_time": "09:00",
            "end_time": "13:00",
            "status": "scheduled",
            "notes": "",
        })
        self.assertRedirects(response, reverse("shift_list"))
        shift = Shift.objects.get(employee=self.employee, client=self.client_obj)
        self.assertEqual(shift.status, "scheduled")
        response = self.client.post(reverse("shift_complete", args=[shift.pk]))
        shift.refresh_from_db()
        self.assertEqual(shift.status, "completed")
