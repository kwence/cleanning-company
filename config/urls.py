from django.contrib import admin
from django.urls import include, path

from core import views as core_views
from payroll import views as payroll_views


def health(request):
    from django.http import JsonResponse

    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("clients/", include("clients.urls")),
    path("employees/", include("employees.urls")),
    path("shifts/", include("shifts.urls")),
    path("timeclock/", include("timeclock.urls")),
    path("badges/", include("badges.urls")),
    path("tasks/", include("tasks.urls")),
    path("payroll/", include("payroll.urls")),
    path("accounting/", include("accounting.urls")),
    path("banking/", include("banking.urls")),
    path("inventory/", include("inventory.urls")),
]
