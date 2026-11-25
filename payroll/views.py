"""Payroll views: run generation, payslip issuing and emailing."""

from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from employees.models import Employee
from .models import PayrollRun, Payslip
from .services import (
    generate_employee_payslip,
    generate_payroll,
    get_payroll_config,
    issue_and_email_run,
    period_bounds,
)
from accounting.models import Payment


@login_required
def payroll_home(request):
    today = date.today()
    period = f"{today.year:04d}-{today.month:02d}"
    run = (
        PayrollRun.objects.filter(period=period)
        .prefetch_related("payslips")
        .order_by("-id")
        .first()
    )
    recent_runs = PayrollRun.objects.prefetch_related("payslips__employee").all()[:6]
    config = get_payroll_config()
    tax_years = [
        (2023, "2023/2024"),
        (2024, "2024/2025"),
        (2025, "2025/2026"),
        (2026, "2026/2027"),
    ]
    context = {
        "period": period,
        "run": run,
        "recent_runs": recent_runs,
        "config": config,
        "tax_years": tax_years,
    }
    return render(request, "payroll/payroll_home.html", context)


@login_required
def payroll_generate(request):
    if request.method == "POST":
        period = request.POST.get("period") or f"{date.today().year:04d}-{date.today().month:02d}"
        run, created = generate_payroll(period)
        messages.success(
            request,
            f"Payroll {period} generated with {run.payslip_count} payslip(s).",
        )
        return redirect("payroll_home")
    return redirect("payroll_home")


@login_required
def payroll_payslip(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    run = payslip.run
    config = get_payroll_config()
    start, _end = period_bounds(payslip.period)
    context = {
        "payslip": payslip,
        "run": run,
        "config": config,
        "period_start": start,
        "auto_print": request.GET.get("print") == "1",
    }
    return render(request, "payroll/payslip_detail.html", context)


@login_required
def payroll_payslip_email(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    results, sent_count, failed_count = issue_and_email_run(payslip.run)
    if sent_count:
        messages.success(request, f"Payroll issued. {sent_count} payslip(s) emailed.")
    if failed_count:
        errors = [r["error"] for r in results if r["error"]]
        detail = f" {errors[0]}" if errors else ""
        messages.warning(
            request,
            f"Payroll issued, but {failed_count} payslip(s) could not be emailed.{detail}",
        )
    if not sent_count and not failed_count:
        messages.info(request, "Payroll issued.")
    return redirect("payslip", pk=payslip.pk)


@login_required
def payroll_mark_paid(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    if request.method == "POST":
        payslip.status = "paid"
        payslip.paid_at = timezone.now()
        payslip.save(update_fields=["status", "paid_at"])
        Payment.objects.get_or_create(
            payslip=payslip,
            defaults={
                "employee": payslip.employee,
                "amount": payslip.net_amount,
                "payment_date": date.today(),
                "method": "bank_transfer",
                "status": "paid",
                "transaction_ref": f"W-{payslip.pay_reference}",
                "paid_at": timezone.now(),
            },
        )
        payslip.run.status = "paid"
        payslip.run.save(update_fields=["status"])
        messages.success(
            request,
            f"Payment of £{payslip.net_amount} marked as paid for {payslip.employee.full_name}.",
        )
    return redirect("payslip", pk=payslip.pk)


@login_required
def payroll_generate_employee(request, employee_pk):
    employee = get_object_or_404(Employee, pk=employee_pk)
    if request.method == "POST":
        period = request.POST.get("period") or f"{date.today().year:04d}-{date.today().month:02d}"
        _run, payslip, created = generate_employee_payslip(employee, period)
        if payslip is None:
            messages.warning(
                request,
                f"Payslip for {employee.full_name} in {period} could not be generated because the payroll run is not draft.",
            )
            return redirect("employee_list")
        if created:
            messages.success(request, f"Payslip generated for {employee.full_name} ({period}).")
        else:
            messages.info(request, f"Payslip for {employee.full_name} ({period}) already exists.")
        return redirect("payslip", pk=payslip.pk)
    return redirect("employee_list")


@login_required
def payroll_config_view(request):
    config = get_payroll_config()
    tax_years = [
        (2023, "2023/2024"),
        (2024, "2024/2025"),
        (2025, "2025/2026"),
        (2026, "2026/2027"),
    ]
    if request.method == "POST":
        config.pay_day = request.POST.get("pay_day") or config.pay_day
        config.overtime_threshold = request.POST.get("overtime_threshold") or config.overtime_threshold
        config.overtime_multiplier = request.POST.get("overtime_multiplier") or config.overtime_multiplier
        config.tax_year = request.POST.get("tax_year") or config.tax_year
        config.save()
        messages.success(request, "Payroll configuration saved.")
        return redirect("payroll_home")
    return render(request, "payroll/payroll_config.html", {"config": config, "tax_years": tax_years})
