"""Cleaning shifts: who cleans which client, when."""

from django.db import models

from clients.models import Client
from employees.models import Employee


class Shift(models.Model):
    STATUS_CHOICES = (
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="shifts")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="shifts")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="scheduled")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["date", "start_time", "-id"]

    def __str__(self):
        return f"{self.employee.full_name} → {self.client.name} ({self.date})"
