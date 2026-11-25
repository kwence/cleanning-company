from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Equipment, StockItem, StockMovement, StockOrder

User = get_user_model()


class InventoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="StrongPass123!")
        self.client.force_login(self.user)
        self.item = StockItem.objects.create(
            name="Bleach", category="detergent", unit="bottle", minimum_stock=Decimal("2"), coshh_required=True
        )

    def test_stock_movement_balance(self):
        StockMovement.objects.create(item=self.item, movement_type="in", quantity=Decimal("10"), movement_date=date.today())
        StockMovement.objects.create(item=self.item, movement_type="out", quantity=Decimal("-3"), movement_date=date.today())
        self.assertEqual(self.item.current_stock, Decimal("7"))

    def test_order_receive_creates_stock_in(self):
        response = self.client.post(reverse("stock_orders"), {
            "item": self.item.pk, "supplier": "Acme", "quantity": "5", "unit_cost": "2.50",
            "order_date": date.today().isoformat(), "expected_date": "", "received_date": date.today().isoformat(),
            "status": "received", "reference": "ORD-1", "notes": "",
        })
        self.assertEqual(response.status_code, 302)
        order = StockOrder.objects.get(reference="ORD-1")
        self.assertEqual(order.status, "received")
        self.assertTrue(StockMovement.objects.filter(item=self.item, reference="ORD-1", movement_type="in").exists())
        self.item.refresh_from_db()
        self.assertEqual(self.item.current_stock, Decimal("5"))

    def test_equipment_safety_flags(self):
        eq = Equipment.objects.create(
            name="Vacuum 1", equipment_type="vacuum", asset_tag="VAC-001",
            status="quarantine", is_safe_to_use=False,
        )
        self.assertTrue(eq.needs_attention)
        response = self.client.get(reverse("equipment_list"))
        self.assertContains(response, "VAC-001")
        self.assertContains(response, "PUWER")