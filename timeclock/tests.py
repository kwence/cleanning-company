"""Tests for the timeclock: clock entries and approvals."""

from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from employees.models import Employee
from .models import TimeEntry

User = get_user_model()


class TimeEntryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="StrongPass123!")
        self.employee = Employee.objects.create(full_name="Maria Gonzalez", hourly_rate=12.5, start_date=date.today(), employment_status="active")

    def test_approve_time_entry(self):
        entry = TimeEntry.objects.create(
            employee=self.employee, date=date.today(), clock_in=time(9, 0), clock_out=time(13, 0), approved=False,
        )
        self.client.force_login(self.user)
        response = self.client.post(reverse("time_entry_approve", args=[entry.pk]))
        entry.refresh_from_db()
        self.assertTrue(entry.approved)
        self.assertEqual(entry.approved_by, self.user)

    def test_timeclock_home_requires_login(self):
        response = self.client.get(reverse("timeclock_home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
