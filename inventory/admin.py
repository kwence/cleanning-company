from django.contrib import admin

from .models import Equipment, StockItem, StockMovement, StockOrder


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "unit", "minimum_stock", "coshh_required", "is_active")
    list_filter = ("category", "coshh_required", "is_active")
    search_fields = ("name", "sku", "supplier")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("item", "movement_type", "quantity", "movement_date", "reference", "recorded_by")
    list_filter = ("movement_type", "movement_date")
    search_fields = ("item__name", "reference")


@admin.register(StockOrder)
class StockOrderAdmin(admin.ModelAdmin):
    list_display = ("item", "supplier", "quantity", "unit_cost", "status", "order_date", "received_date")
    list_filter = ("status", "order_date")
    search_fields = ("item__name", "supplier", "reference")


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name", "equipment_type", "asset_tag", "status", "is_safe_to_use", "next_service_date", "pat_due_date")
    list_filter = ("equipment_type", "status", "is_safe_to_use")
    search_fields = ("name", "asset_tag", "serial_number")