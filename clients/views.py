"""Client (jobsite) management views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClientForm
from .models import Client


@login_required
def client_list(request):
    clients = Client.objects.all()
    status = request.GET.get("status", "")
    query = request.GET.get("q", "").strip()
    if status:
        clients = clients.filter(status=status)
    if query:
        clients = clients.filter(
            Q(name__icontains=query)
            | Q(contact_name__icontains=query)
            | Q(email__icontains=query)
        )
    return render(
        request,
        "clients/client_list.html",
        {"clients": clients, "statuses": Client.STATUS_CHOICES, "status": status, "query": query},
    )


@login_required
def client_form_view(request, pk=None):
    client = get_object_or_404(Client, pk=pk) if pk else None
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client saved.")
            return redirect("client_list")
    else:
        form = ClientForm(instance=client)
    return render(request, "clients/client_form.html", {"form": form, "client": client})


@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        client.delete()
        messages.success(request, "Client deleted.")
        return redirect("client_list")
    return render(request, "clients/client_confirm_delete.html", {"client": client})
