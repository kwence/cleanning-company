"""Tests for client management."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Client

User = get_user_model()


class ClientViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="StrongPass123!")

    def test_client_crud(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("client_create"), {
            "name": "Riverside Care Home",
            "contact_name": "Jane Smith",
            "email": "jane@riversidecare.org",
            "phone": "01234 567890",
            "address": "12 Riverside Walk, London",
            "notes": "Hoist access",
            "status": "active",
        })
        self.assertRedirects(response, reverse("client_list"))
        self.assertTrue(Client.objects.filter(name="Riverside Care Home").exists())

        client = Client.objects.get(name="Riverside Care Home")
        response = self.client.post(reverse("client_edit", args=[client.pk]), {
            "name": "Riverside Care Home",
            "contact_name": "Jane Smith",
            "email": "jane@riversidecare.org",
            "phone": "01234 567890",
            "address": "12 Riverside Walk, London",
            "notes": "Hoist access",
            "status": "inactive",
        })
        self.assertRedirects(response, reverse("client_list"))
        client.refresh_from_db()
        self.assertEqual(client.status, "inactive")

    def test_client_delete_requires_confirmation(self):
        client = Client.objects.create(name="Maple Dental", status="active")
        self.client.force_login(self.user)
        response = self.client.get(reverse("client_delete", args=[client.pk]))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse("client_delete", args=[client.pk]))
        self.assertRedirects(response, reverse("client_list"))
        self.assertFalse(Client.objects.filter(pk=client.pk).exists())
