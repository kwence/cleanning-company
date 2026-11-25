"""Tests for the CleanSweep core app: auth and dashboard."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class CoreAuthTests(TestCase):
    def test_login_page_renders(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign in to CleanSweep")

    def test_register_page_renders(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_login_and_logout_flow(self):
        User.objects.create_user(username="staff1", password="StrongPass123!", email="staff1@example.com")
        self.client.post(reverse("login"), {"username": "staff1", "password": "StrongPass123!"})
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CleanSweep")

    def test_logout_requires_post(self):
        from django.contrib.auth.models import AnonymousUser  # noqa: F401

        User.objects.create_user(username="staff2", password="StrongPass123!")
        self.client.force_login(User.objects.get(username="staff2"))
        self.assertEqual(self.client.get(reverse("logout")).status_code, 403)
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="StrongPass123!", email="manager@example.com")

    def test_dashboard_shows_kpis_for_logged_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shifts scheduled")
        self.assertContains(response, "Payroll")
