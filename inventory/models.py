"""Cleaning stock and equipment management with UK safety/compliance fields."""

from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db import models


class StockItem(models.Model):
    CATEGORY_CHOICES = (
        ("detergent", "Detergent / Cleaning Chemical"),
        ("disinfectant", "Disinfectant / Sanitiser"),
        ("mop", "Mop / Bucket"),
        ("brush", "Brush / Broom"),
        ("cloth", "Cloth / Microfibre"),
        ("cream", "Cream / Polish"),
        ("ppe", "PPE"),
        ("consumable", "Consumable"),
        ("other", "Other"),
    )
    UNIT_CHOICES = (
        ("unit", "Unit"),
        ("bottle", "Bottle"),
        ("pack", "Pack"),
        ("box", "Box"),
        ("litre", "Litre"),
        ("kg", "Kg"),
        ("pair", "Pair"),
    )

    name = models.CharField(max_length=140)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    sku = models.CharField(max_length=40, blank=True, default="")
    unit = models.CharField(max_length=12, choices=UNIT_CHOICES, default="unit")
    supplier = models.CharField(max_length=140, blank=True, default="")
    location = models.CharField(max_length=120, blank=True, default="")
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reorder_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coshh_required = models.BooleanField(default=False, help_text="Chemical requires COSHH assessment/SDS.")
    sds_url = models.URLField(blank=True, default="", help_text="Safety Data Sheet link/location reference.")
    hazard_notes = models.TextField(blank=True, default="")
    ppe_notes = models.TextField(blank=True, default="")
    storage_notes = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def current_stock(self):
        total = self.movements.aggregate(total=models.Sum("quantity")).get("total")
        return total if total is not None else Decimal("0.00")

    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock


class StockMovement(models.Model):
    MOVEMENT_CHOICES = (
        ("in", "Stock In"),
        ("out", "Stock Out"),
        ("adjustment", "Adjustment"),
    )

    item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=12, choices=MOVEMENT_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    movement_date = models.DateField(default=date.today)
    reference = models.CharField(max_length=80, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="stock_movements"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-movement_date", "-id"]

    def __str__(self):
        return f"{self.get_movement_type_display()} · {self.item.name} · {self.quantity}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.quantity == 0:
            raise ValidationError({"quantity": "Quantity cannot be zero."})
        if self.movement_type == "out" and self.quantity > 0:
            self.quantity = -abs(self.quantity)
        if self.movement_type == "in" and self.quantity < 0:
            self.quantity = abs(self.quantity)


class StockOrder(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("ordered", "Ordered"),
        ("received", "Received"),
        ("cancelled", "Cancelled"),
    )

    item = models.ForeignKey(StockItem, on_delete=models.PROTECT, related_name="orders")
    supplier = models.CharField(max_length=140, blank=True, default="")
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_date = models.DateField(default=date.today)
    expected_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="draft")
    reference = models.CharField(max_length=80, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="stock_orders"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-order_date", "-id"]

    def __str__(self):
        return f"Order {self.reference or self.pk} · {self.item.name}"

    @property
    def total_cost(self):
        return (self.quantity or Decimal("0")) * (self.unit_cost or Decimal("0"))


class Equipment(models.Model):
    EQUIPMENT_TYPE_CHOICES = (
        ("vacuum", "Vacuum"),
        ("scrubber", "Floor Scrubber"),
        ("carpet_cleaner", "Carpet Cleaner"),
        ("steam_cleaner", "Steam Cleaner"),
        ("blower", "Blower / Dryer"),
        ("other", "Other"),
    )
    STATUS_CHOICES = (
        ("available", "Available"),
        ("in_use", "In Use"),
        ("maintenance", "Maintenance"),
        ("quarantine", "Quarantined / Unsafe"),
        ("retired", "Retired"),
    )

    name = models.CharField(max_length=140)
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPE_CHOICES, default="other")
    asset_tag = models.CharField(max_length=60, unique=True)
    serial_number = models.CharField(max_length=80, blank=True, default="")
    location = models.CharField(max_length=120, blank=True, default="")
    assigned_to = models.ForeignKey(
        "employees.Employee", on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_equipment"
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="available")
    purchase_date = models.DateField(null=True, blank=True)
    last_service_date = models.DateField(null=True, blank=True)
    next_service_date = models.DateField(null=True, blank=True)
    pat_test_date = models.DateField(null=True, blank=True, help_text="Portable Appliance Testing date.")
    pat_due_date = models.DateField(null=True, blank=True)
    risk_assessment_date = models.DateField(null=True, blank=True)
    puwer_inspection_date = models.DateField(null=True, blank=True, help_text="PUWER inspection/check date.")
    is_safe_to_use = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.asset_tag})"

    @property
    def is_pat_overdue(self):
        return bool(self.pat_due_date and self.pat_due_date < date.today())

    @property
    def is_service_overdue(self):
        return bool(self.next_service_date and self.next_service_date < date.today())

    @property
    def needs_attention(self):
        return (not self.is_safe_to_use) or self.is_pat_overdue or self.is_service_overdue or self.status == "quarantine"