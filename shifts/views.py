"""Shift scheduling views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from clients.models import Client
from employees.models import Employee
from .forms import ShiftForm
from .models import Shift


@login_required
def shift_list(request):
    shifts = Shift.objects.select_related("employee", "client").all()
    status = request.GET.get("status", "")
    employee = request.GET.get("employee", "")
    query = request.GET.get("q", "").strip()
    if status:
        shifts = shifts.filter(status=status)
    if employee:
        shifts = shifts.filter(employee_id=employee)
    if query:
        shifts = shifts.filter(
            Q(client__name__icontains=query) | Q(employee__full_name__icontains=query)
        )
    return render(
        request,
        "shifts/shift_list.html",
        {
            "shifts": shifts,
            "statuses": Shift.STATUS_CHOICES,
            "status": status,
            "employees": Employee.objects.all(),
            "employee": employee,
            "selected_employee": employee,
            "query": query,
        },
    )


@login_required
def shift_create(request):
    if request.method == "POST":
        form = ShiftForm(request.POST)
        if form.is_valid():
            shift = form.save()
            messages.success(request, "Shift scheduled.")
            return redirect("shift_list")
    else:
        form = ShiftForm()
    return render(request, "shifts/shift_form.html", {"form": form})


@login_required
def shift_edit(request, pk):
    shift = get_object_or_404(Shift, pk=pk)
    if request.method == "POST":
        form = ShiftForm(request.POST, instance=shift)
        if form.is_valid():
            shift = form.save()
            messages.success(request, "Shift updated.")
            return redirect("shift_list")
    else:
        form = ShiftForm(instance=shift)
    return render(request, "shifts/shift_form.html", {"form": form, "shift": shift})


@login_required
def shift_delete(request, pk):
    shift = get_object_or_404(Shift, pk=pk)
    if request.method == "POST":
        shift.delete()
        messages.success(request, "Shift deleted.")
        return redirect("shift_list")
    return render(request, "shifts/shift_confirm_delete.html", {"shift": shift})


@login_required
def shift_complete(request, pk):
    shift = get_object_or_404(Shift, pk=pk)
    if request.method == "POST":
        shift.status = "completed"
        shift.completed_at = shift.completed_at or timezone.now()
        shift.save(update_fields=["status", "completed_at"])
        messages.success(request, "Shift marked as completed.")
    return redirect("shift_list")
