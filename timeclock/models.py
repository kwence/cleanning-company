"""Time tracking: clock in / clock out entries with manager approval."""

from datetime import datetime

from django.conf import settings
from django.db import models


class TimeEntry(models.Model):
    """A clock in/out record; completed entries wait for manager approval."""

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="time_entries"
    )
    shift = models.ForeignKey(
        "shifts.Shift", on_delete=models.SET_NULL, null=True, blank=True, related_name="time_entries"
    )
    date = models.DateField()
    clock_in = models.TimeField()
    clock_out = models.TimeField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_time_entries"
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-clock_in", "-id"]

    def __str__(self):
        return f"{self.employee.full_name} {self.date} {self.clock_in}"

    @property
    def duration_hours(self):
        if not self.clock_in or not self.clock_out:
            return 0
        delta = datetime.combine(self.date, self.clock_out) - datetime.combine(self.date, self.clock_in)
        return max(0.0, delta.total_seconds() / 3600.0)
