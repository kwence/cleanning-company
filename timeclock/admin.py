from django.contrib import admin

from .models import TimeEntry


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "clock_in", "clock_out", "approved", "approved_at")
    list_filter = ("approved", "date")
    list_select_related = ("employee",)
    date_hierarchy = "date"
