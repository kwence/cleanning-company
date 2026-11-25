"""Task (cleaning checklist) views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import TaskForm
from .models import Task


@login_required
def task_list(request):
    tasks = Task.objects.select_related("client", "employee", "shift").all()
    status = request.GET.get("status", "")
    if status:
        tasks = tasks.filter(status=status)
    return render(
        request,
        "tasks/task_list.html",
        {"tasks": tasks, "statuses": Task.STATUS_CHOICES, "status": status},
    )


@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, "Task created.")
            return redirect("task_list")
    else:
        form = TaskForm()
    return render(request, "tasks/task_form.html", {"form": form})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            messages.success(request, "Task updated.")
            return redirect("task_list")
    else:
        form = TaskForm(instance=task)
    return render(request, "tasks/task_form.html", {"form": form, "task": task})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted.")
        return redirect("task_list")
    return render(request, "tasks/task_confirm_delete.html", {"task": task})


@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        task.status = "completed"
        task.completed_at = task.completed_at or timezone.now()
        task.save(update_fields=["status", "completed_at"])
        messages.success(request, f"Task '{task.title}' completed.")
    return redirect("task_list")
