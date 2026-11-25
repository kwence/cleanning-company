"""Inventory and equipment management views."""

from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EquipmentForm, StockItemForm, StockMovementForm, StockOrderForm
from .models import Equipment, StockItem, StockMovement, StockOrder


@login_required
def stock_list(request):
    items = StockItem.objects.prefetch_related("movements").all()
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    if q:
        items = items.filter(name__icontains=q)
    if category:
        items = items.filter(category=category)
    low_stock = [i for i in items if i.is_active and i.is_low_stock]
    return render(request, "inventory/stock_list.html", {
        "items": items,
        "q": q,
        "category": category,
        "categories": StockItem.CATEGORY_CHOICES,
        "low_stock_count": len(low_stock),
    })


@login_required
def stock_item_create(request):
    form = StockItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save()
        messages.success(request, f"Stock item '{item.name}' created.")
        return redirect("stock_list")
    return render(request, "inventory/stock_item_form.html", {"form": form})


@login_required
def stock_item_edit(request, pk):
    item = get_object_or_404(StockItem, pk=pk)
    form = StockItemForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Stock item '{item.name}' updated.")
        return redirect("stock_list")
    return render(request, "inventory/stock_item_form.html", {"form": form, "item": item})


@login_required
def stock_movements(request):
    movements = StockMovement.objects.select_related("item", "recorded_by").all()
    item_id = request.GET.get("item", "")
    movement_type = request.GET.get("type", "")
    if item_id:
        movements = movements.filter(item_id=item_id)
    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    form = StockMovementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        movement = form.save(commit=False)
        movement.recorded_by = request.user
        movement.save()
        messages.success(request, f"Stock movement recorded for {movement.item.name}.")
        return redirect("stock_movements")

    totals = StockItem.objects.filter(is_active=True).aggregate(
        in_qty=Sum("movements__quantity", filter=models_Q_in()),
    )
    # simple totals
    in_total = StockMovement.objects.filter(movement_type="in").aggregate(t=Sum("quantity"))["t"] or 0
    out_total = StockMovement.objects.filter(movement_type="out").aggregate(t=Sum("quantity"))["t"] or 0
    return render(request, "inventory/stock_movements.html", {
        "movements": movements[:200],
        "form": form,
        "items": StockItem.objects.filter(is_active=True),
        "movement_types": StockMovement.MOVEMENT_CHOICES,
        "selected_item": item_id,
        "selected_type": movement_type,
        "in_total": in_total,
        "out_total": out_total,
    })


def models_Q_in():
    from django.db.models import Q
    return Q(movements__movement_type="in")


@login_required
def stock_orders(request):
    orders = StockOrder.objects.select_related("item", "created_by").all()
    status = request.GET.get("status", "")
    if status:
        orders = orders.filter(status=status)
    form = StockOrderForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        order = form.save(commit=False)
        order.created_by = request.user
        if not order.supplier:
            order.supplier = order.item.supplier
        if order.status == "received" and not order.received_date:
            order.received_date = date.today()
        order.save()
        # Auto-create stock-in movement when received and not already recorded for this ref.
        if order.status == "received":
            ref = order.reference or f"ORDER-{order.pk}"
            if not StockMovement.objects.filter(reference=ref, item=order.item, movement_type="in").exists():
                StockMovement.objects.create(
                    item=order.item,
                    movement_type="in",
                    quantity=abs(order.quantity),
                    movement_date=order.received_date or date.today(),
                    reference=ref,
                    notes=f"Auto-received from order {ref}",
                    recorded_by=request.user,
                )
        messages.success(request, f"Stock order saved for {order.item.name}.")
        return redirect("stock_orders")
    return render(request, "inventory/stock_orders.html", {
        "orders": orders[:200],
        "form": form,
        "statuses": StockOrder.STATUS_CHOICES,
        "selected_status": status,
    })


@login_required
def stock_order_receive(request, pk):
    order = get_object_or_404(StockOrder, pk=pk)
    if request.method == "POST" and order.status != "received":
        order.status = "received"
        order.received_date = date.today()
        order.save(update_fields=["status", "received_date"])
        ref = order.reference or f"ORDER-{order.pk}"
        if not StockMovement.objects.filter(reference=ref, item=order.item, movement_type="in").exists():
            StockMovement.objects.create(
                item=order.item,
                movement_type="in",
                quantity=abs(order.quantity),
                movement_date=order.received_date,
                reference=ref,
                notes=f"Auto-received from order {ref}",
                recorded_by=request.user,
            )
        messages.success(request, f"Order for {order.item.name} marked received and stock updated.")
    return redirect("stock_orders")


@login_required
def equipment_list(request):
    equipment = Equipment.objects.select_related("assigned_to").all()
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if q:
        equipment = equipment.filter(name__icontains=q)
    if status:
        equipment = equipment.filter(status=status)
    attention = [e for e in equipment if e.needs_attention]
    return render(request, "inventory/equipment_list.html", {
        "equipment": equipment,
        "q": q,
        "status": status,
        "statuses": Equipment.STATUS_CHOICES,
        "attention_count": len(attention),
    })


@login_required
def equipment_create(request):
    form = EquipmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        eq = form.save()
        messages.success(request, f"Equipment '{eq.name}' added.")
        return redirect("equipment_list")
    return render(request, "inventory/equipment_form.html", {"form": form})


@login_required
def equipment_edit(request, pk):
    eq = get_object_or_404(Equipment, pk=pk)
    form = EquipmentForm(request.POST or None, instance=eq)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Equipment '{eq.name}' updated.")
        return redirect("equipment_list")
    return render(request, "inventory/equipment_form.html", {"form": form, "equipment": eq})