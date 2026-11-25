"""Tests for cleaning tasks."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clients.models import Client
from tasks.models import Task

User = get_user_model()


class TaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="StrongPass123!")
        self.client_obj = Client.objects.create(name="Riverside Care Home", status="active")

    def test_task_complete(self):
        task = Task.objects.create(client=self.client_obj, title="Deep clean lounge", status="open")
        self.client.force_login(self.user)
        response = self.client.post(reverse("task_complete", args=[task.pk]))
        task.refresh_from_db()
        self.assertEqual(task.status, "completed")
        self.assertIsNotNone(task.completed_at)
