"""Timeclock views: clock in, clock out, approve entries."""

from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from employees.models import Employee
from shifts.models import Shift
from .models import TimeEntry


@login_required
def timeclock_home(request):
    today = date.today()
    open_entries = (
        TimeEntry.objects.filter(clock_out__isnull=True)
        .select_related("employee")
        .order_by("created_at")
    )
    today_entries = (
        TimeEntry.objects.filter(date=today)
        .select_related("employee", "shift")
        .order_by("clock_in")
    )
    employees = Employee.objects.filter(employment_status="active").all()
    context = {
        "open_entries": open_entries,
        "today_entries": today_entries,
        "employees": employees,
        "today": today,
    }
    return render(request, "timeclock/timeclock_home.html", context)


@login_required
def time_entry_list(request):
    entries = TimeEntry.objects.select_related("employee", "shift").all()
    pending = request.GET.get("pending") == "1"
    if pending:
        entries = entries.filter(approved=False, clock_out__isnull=False)
    return render(
        request,
        "timeclock/time_entry_list.html",
        {"entries": entries, "pending_only": pending},
    )


@login_required
def time_entry_clock_in(request):
    """Start a new open time entry for an employee."""
    if request.method == "POST":
        employee_id = request.POST.get("employee")
        employee = Employee.objects.filter(pk=employee_id).first()
        if employee is None:
            messages.error(request, "Please choose an employee to clock in.")
        else:
            if TimeEntry.objects.filter(employee=employee, clock_out__isnull=True).exists():
                messages.warning(request, f"{employee.full_name} already has an open time entry.")
            else:
                TimeEntry.objects.create(
                    employee=employee,
                    date=request.POST.get("date") or date.today().isoformat(),
                    clock_in=timezone.now().time(),
                    approved=False,
                )
                messages.success(request, f"Clocked in {employee.full_name}.")
    return redirect("timeclock_home")


@login_required
def time_entry_clock_out(request, pk):
    entry = get_object_or_404(TimeEntry, pk=pk)
    if request.method == "POST":
        entry.clock_out = timezone.now().time()
        entry.save(update_fields=["clock_out"])
        messages.success(request, f"Clocked out for {entry.employee.full_name}.")
    return redirect("timeclock_home")


@login_required
def time_entry_approve(request, pk):
    entry = get_object_or_404(TimeEntry, pk=pk)
    if request.method == "POST":
        entry.approved = True
        entry.approved_at = timezone.now()
        entry.approved_by = request.user
        entry.save(update_fields=["approved", "approved_at", "approved_by"])
        messages.success(request, f"Approved {entry.employee.full_name}'s time entry.")
    return redirect("time_entry_list")


@login_required
def time_entry_delete(request, pk):
    entry = get_object_or_404(TimeEntry, pk=pk)
    if request.method == "POST":
        entry.delete()
        messages.success(request, "Time entry deleted.")
    return redirect("time_entry_list")
