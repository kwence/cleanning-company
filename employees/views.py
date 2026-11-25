"""Employee and certification management views."""

from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from payroll.models import Payslip

from .forms import EmployeeCertFormSet, EmployeeForm
from .models import Employee


@login_required
def employee_list(request):
    employees = Employee.objects.select_related("user").all()
    status = request.GET.get("status", "")
    query = request.GET.get("q", "").strip()
    period = request.GET.get("period") or f"{date.today().year:04d}-{date.today().month:02d}"
    if status:
        employees = employees.filter(employment_status=status)
    if query:
        employees = employees.filter(
            Q(full_name__icontains=query) | Q(email__icontains=query)
        )
    payslips_by_employee = {
        p.employee_id: p
        for p in Payslip.objects.filter(period=period, employee__in=employees).select_related("employee")
    }
    return render(
        request,
        "employees/employee_list.html",
        {
            "employees": employees,
            "statuses": Employee.EMPLOYMENT_STATUS_CHOICES,
            "status": status,
            "query": query,
            "period": period,
            "payslips_by_employee": payslips_by_employee,
        },
    )


@login_required
def employee_form_view(request, pk=None):
    employee = get_object_or_404(Employee, pk=pk) if pk else None
    form = EmployeeForm(request.POST or None, instance=employee)
    formset = None
    if employee is not None and request.method == "POST":
        formset = EmployeeCertFormSet(request.POST, instance=employee)
    elif employee is not None:
        formset = EmployeeCertFormSet(instance=employee)

    if request.method == "POST":
        valid = form.is_valid()
        if employee is not None and formset is not None:
            valid = valid and formset.is_valid()
        if valid:
            employee = form.save()
            if formset is not None and employee is not None:
                formset.instance = employee
                formset.save()
            messages.success(request, "Employee saved.")
            return redirect("employee_list")
    return render(
        request,
        "employees/employee_form.html",
        {"form": form, "employee": employee, "formset": formset},
    )


@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        employee.delete()
        messages.success(request, "Employee deleted.")
        return redirect("employee_list")
    return render(request, "employees/employee_confirm_delete.html", {"employee": employee})
