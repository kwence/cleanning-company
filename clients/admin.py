from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_name", "email", "phone", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "contact_name", "email", "address")
