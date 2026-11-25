from django.contrib import admin

from .models import Shift


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("date", "start_time", "end_time", "employee", "client", "status")
    list_filter = ("status", "date")
    list_select_related = ("employee", "client")
    date_hierarchy = "date"
