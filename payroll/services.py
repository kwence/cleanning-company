"""UK payroll calculations, payroll run generation and payslip emailing."""

from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

from accounting.models import Payment
from employees.models import Employee
from payroll.models import PayrollConfig, PayrollRun, Payslip
from timeclock.models import TimeEntry

ZERO = Decimal("0.00")

# UK 2025/26 tax year constants (HMRC rates).
PERSONAL_ALLOWANCE = Decimal("12570")
BASIC_RATE = Decimal("0.20")
BASIC_THRESHOLD = Decimal("50270")
HIGHER_RATE = Decimal("0.40")
HIGHER_THRESHOLD = Decimal("125140")
ADDITIONAL_RATE = Decimal("0.45")
NI_RATE = Decimal("0.08")
NI_UPPER_RATE = Decimal("0.02")
NI_THRESHOLD = Decimal("12570")
NI_UPPER_THRESHOLD = Decimal("50270")
EMPLOYER_NIC_RATE = Decimal("0.138")
CIS_RATE = Decimal("0.20")


def get_payroll_config():
    config, _ = PayrollConfig.objects.get_or_create(
        pk=1,
        defaults={
            "pay_day": 28,
            "overtime_threshold": 40,
            "overtime_multiplier": Decimal("1.5"),
            "tax_year": 2025,
            "pay_frequency": "monthly",
        },
    )
    return config


def tax_year_for(day):
    """HMRC tax year label for a date (2025 means 2025/26, starting 6 April)."""
    return day.year if (day.month, day.day) >= (4, 6) else day.year - 1


def income_tax(gross, tax_year):
    """Income Tax for an employee using the 2025/26 bands."""
    allowance = PERSONAL_ALLOWANCE
    taxable = max(ZERO, gross - allowance)
    tax = ZERO
    if taxable <= 0:
        return ZERO
    basic_band = min(taxable, BASIC_THRESHOLD - PERSONAL_ALLOWANCE)
    tax += basic_band * BASIC_RATE
    taxable -= basic_band
    if taxable > 0:
        higher_band = min(taxable, HIGHER_THRESHOLD - BASIC_THRESHOLD)
        tax += higher_band * HIGHER_RATE
        taxable -= higher_band
        if taxable > 0:
            tax += taxable * ADDITIONAL_RATE
    return tax


def employee_ni(gross, tax_year):
    """Employee National Insurance for the 2025/26 year."""
    if gross <= NI_THRESHOLD:
        return ZERO
    employee_nic = (min(gross, NI_UPPER_THRESHOLD) - NI_THRESHOLD) * NI_RATE
    if gross > NI_UPPER_THRESHOLD:
        employee_nic += (gross - NI_UPPER_THRESHOLD) * NI_UPPER_RATE
    return employee_nic


def employer_nic(gross, tax_year):
    """Employer National Insurance calculated automatically at 13.8% of gross pay."""
    if gross <= ZERO:
        return ZERO
    return (gross * EMPLOYER_NIC_RATE).quantize(Decimal("0.01"))


def period_bounds(period):
    """Return (start_date, end_date) for a YYYY-MM pay period."""
    year, month = (int(part) for part in str(period).split("-"))
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


def calculate_employee_pay(employee, period_start, period_end, config):
    """Gross pay from salary or approved time entries, with weekly overtime."""
    tax_year = config.tax_year
    is_cis = bool(employee.is_cis)

    if employee.salary_monthly:
        # Salaried employee: gross pay is the fixed monthly salary.
        gross = employee.salary_monthly
        regular_hours = ZERO
        overtime_hours = ZERO
        overtime_pay = ZERO
        tax = ZERO
        ni = ZERO
        if is_cis:
            net = gross - (gross * CIS_RATE)
            cis = gross * CIS_RATE
        else:
            tax = income_tax(gross, tax_year)
            ni = employee_ni(gross, tax_year)
            net = gross - tax - ni
            cis = ZERO
        nic = employer_nic(gross, tax_year)
        return {
            "hours": regular_hours,
            "gross": gross,
            "overtime_hours": overtime_hours,
            "overtime_pay": overtime_pay,
            "tax": tax,
            "ni": ni,
            "net": net,
            "employer_nic": nic,
            "cis": cis,
        }

    entries = (
        TimeEntry.objects.filter(
            employee=employee,
            approved=True,
            clock_out__isnull=False,
            date__gte=period_start,
            date__lte=period_end,
        )
        .select_related("employee")
        .order_by("date", "clock_in")
    )

    weekly_hours = {}
    for entry in entries:
        week_start = entry.date - timedelta(days=entry.date.weekday())
        weekly_hours[week_start] = weekly_hours.get(week_start, Decimal("0")) + Decimal(str(entry.duration_hours))

    rate = employee.hourly_rate
    threshold = Decimal(config.overtime_threshold)
    multiplier = config.overtime_multiplier
    gross = ZERO
    regular_hours = ZERO
    overtime_hours = ZERO
    overtime_pay = ZERO
    for week_start in sorted(weekly_hours):
        hours = weekly_hours[week_start]
        reg = min(hours, threshold)
        ot = max(Decimal("0"), hours - threshold)
        regular_hours += reg
        overtime_hours += ot
        overtime_pay += ot * rate * multiplier
    gross = regular_hours * rate + overtime_pay

    tax = income_tax(gross, tax_year)
    ni = employee_ni(gross, tax_year)
    net = gross - tax - ni
    cis = ZERO
    if is_cis:
        cis = gross * CIS_RATE
        net = gross - cis
        tax = ZERO
        ni = ZERO
    nic = employer_nic(gross, tax_year)

    return {
        "hours": regular_hours + overtime_hours,
        "gross": gross,
        "overtime_hours": overtime_hours,
        "overtime_pay": overtime_pay,
        "tax": tax,
        "ni": ni,
        "net": net,
        "employer_nic": nic,
        "cis": cis,
    }


def _refresh_run_totals(run):
    payslips = list(run.payslips.all())
    run.gross_total = sum((p.gross_amount for p in payslips), ZERO)
    run.deductions_total = sum((p.tax_amount + p.ni_amount + p.cis_amount for p in payslips), ZERO)
    run.net_total = sum((p.net_amount for p in payslips), ZERO)
    run.employer_nic_total = sum((p.employer_nic for p in payslips), ZERO)
    run.payslip_count = len(payslips)
    run.save(
        update_fields=[
            "gross_total",
            "deductions_total",
            "net_total",
            "employer_nic_total",
            "payslip_count",
        ]
    )
    return run


def _build_payslip(run, employee, period, config):
    period_start, period_end = period_bounds(period)
    pay = calculate_employee_pay(employee, period_start, period_end, config)
    return Payslip(
        run=run,
        employee=employee,
        period=period,
        gross_amount=pay["gross"],
        overtime_hours=pay["overtime_hours"],
        overtime_pay=pay["overtime_pay"],
        tax_amount=pay["tax"],
        ni_amount=pay["ni"],
        net_amount=pay["net"],
        employer_nic=pay["employer_nic"],
        cis_amount=pay["cis"],
        pay_reference=f"PS-{period}-{employee.pk:04d}",
        status="draft",
    )


def generate_payroll(period, config=None):
    """Create (or refresh) a payroll run and its payslips for a YYYY-MM period."""
    config = config or get_payroll_config()
    period_start, period_end = period_bounds(period)
    run, created = PayrollRun.objects.get_or_create(period=period, defaults={"status": "draft"})
    if not created:
        if run.status != "draft":
            return run, False
        run.payslips.all().delete()
    run.status = "draft"
    run.generated_at = timezone.now()
    run.save(update_fields=["status", "generated_at"])

    payslips = []
    for employee in Employee.objects.filter(employment_status="active").select_related("user"):
        has_entries = TimeEntry.objects.filter(
            employee=employee,
            approved=True,
            clock_out__isnull=False,
            date__gte=period_start,
            date__lte=period_end,
        ).exists()
        # Salaried employees are paid even without clocked entries; hourly ones need hours.
        if not employee.salary_monthly and not has_entries:
            continue
        payslip = _build_payslip(run, employee, period, config)
        payslip.save()
        payslips.append(payslip)

    _refresh_run_totals(run)
    return run, created


def generate_employee_payslip(employee, period, config=None):
    """Generate or refresh a single employee's payslip for a period.

    Creates the payroll run if needed. If the run is not draft, the existing
    payslip is returned unchanged.
    """
    config = config or get_payroll_config()
    run, _ = PayrollRun.objects.get_or_create(period=period, defaults={"status": "draft"})
    existing = run.payslips.filter(employee=employee).first()
    if run.status != "draft":
        return run, existing, False

    if existing:
        existing.delete()

    payslip = _build_payslip(run, employee, period, config)
    payslip.save()
    run.status = "draft"
    run.generated_at = timezone.now()
    run.save(update_fields=["status", "generated_at"])
    _refresh_run_totals(run)
    return run, payslip, True


def send_payslip_email(payslip):
    """Email a payslip to the employee.

    Returns (sent: bool, error: str|None).
    """
    employee = payslip.employee
    if not employee.email:
        return False, "Employee has no email address."

    period_start, period_end = period_bounds(payslip.period)
    context = {
        "payslip": payslip,
        "employee": employee,
        "period": payslip.period,
        "period_label": f"{period_start.strftime('%B %Y')}",
        "tax_year": get_payroll_config().tax_year,
        "cis_amount": payslip.cis_amount,
    }
    body = render_to_string("payroll/payslip_email.txt", context)
    email = EmailMessage(
        subject=f"Your payslip {payslip.pay_reference} - {payslip.period}",
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[employee.email],
    )
    try:
        sent = email.send(fail_silently=False)
        return bool(sent), None
    except Exception as exc:
        return False, str(exc)


def issue_and_email_run(run):
    """Mark a run as issued and email every draft payslip.

    Returns (results, sent_count, failed_count).
    """
    results = []
    sent_count = 0
    failed_count = 0
    for payslip in run.payslips.select_related("employee").all():
        payslip.status = "issued"
        payslip.issued_at = timezone.now()
        payslip.save(update_fields=["status", "issued_at"])
        error = None
        sent = False
        if payslip.employee.email:
            sent, error = send_payslip_email(payslip)
            if sent:
                payslip.status = "emailed"
                payslip.emailed_at = timezone.now()
                payslip.save(update_fields=["status", "emailed_at"])
                sent_count += 1
            else:
                failed_count += 1
        else:
            error = "Employee has no email address."
            failed_count += 1
        results.append({"payslip": payslip, "sent": sent, "error": error})
    run.status = "issued"
    run.save(update_fields=["status"])
    return results, sent_count, failed_count
