"""Dashboard, authentication and home views for the cleaning company."""

from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from badges.models import CleaningBadge
from employees.models import Employee
from shifts.models import Shift
from tasks.models import Task
from timeclock.models import TimeEntry

from .forms import LoginForm, RegistrationForm


def home(request):
    return redirect("dashboard")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                next_url = request.POST.get("next", "")
                if next_url and request.path != next_url:
                    return redirect(next_url)
                return redirect("dashboard")
    else:
        form = LoginForm(request)
    return render(request, "registration/login.html", {"form": form})


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            from employees.models import Employee

            Employee.objects.create(user=user, full_name=user.username)
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account is ready.")
            return redirect("dashboard")
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been signed out.")
        return redirect("login")
    return HttpResponseForbidden("Use the sign out button to leave your account.")


@login_required
def compliance(request):
    employees = Employee.objects.all().order_by("full_name")
    return render(request, "core/compliance.html", {"employees": employees})


@login_required
def dashboard(request):
    today = date.today()

    today_shifts = (
        Shift.objects.filter(date=today)
        .select_related("employee", "client")
        .order_by("start_time")
    )
    in_progress = today_shifts.filter(status="in_progress")
    scheduled_today = today_shifts.filter(status="scheduled")

    pending_entries = (
        TimeEntry.objects.filter(approved=False, clock_out__isnull=False)
        .select_related("employee")
        .order_by("-date", "-id")[:8]
    )
    pending_count = TimeEntry.objects.filter(approved=False, clock_out__isnull=False).count()

    open_tasks = (
        Task.objects.filter(status="open")
        .select_related("client", "employee")
        .order_by("due_date", "id")[:6]
    )
    upcoming = (
        Shift.objects.filter(date__gte=today, status="scheduled")
        .select_related("employee", "client")
        .order_by("date", "start_time")[:7]
    )
    unexpired_badges = (
        CleaningBadge.objects.filter(status="active").select_related("employee").count()
    )

    payroll_period = f"{today.year:04d}-{today.month:02d}"
    payroll_run = None
    try:
        from payroll.models import PayrollRun

        payroll_run = PayrollRun.objects.filter(period=payroll_period).order_by("-id").first()
    except Exception:  # pragma: no cover - defensive while apps are still wiring up
        payroll_run = None

    context = {
        "today": today,
        "today_shifts": today_shifts,
        "in_progress": in_progress,
        "scheduled_today": scheduled_today,
        "pending_entries": pending_entries,
        "pending_count": pending_count,
        "open_tasks": open_tasks,
        "upcoming": upcoming,
        "active_badge_count": unexpired_badges,
        "payroll_period": payroll_period,
        "payroll_run": payroll_run,
    }
    return render(request, "core/dashboard.html", context)
