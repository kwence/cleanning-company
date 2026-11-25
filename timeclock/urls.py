from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.timeclock_home, name="timeclock_home"),
    path("entries/", views.time_entry_list, name="time_entry_list"),
    path("clock-in/", views.time_entry_clock_in, name="time_entry_clock_in"),
    path("<int:pk>/clock-out/", views.time_entry_clock_out, name="time_entry_clock_out"),
    path("<int:pk>/approve/", views.time_entry_approve, name="time_entry_approve"),
    path("<int:pk>/delete/", views.time_entry_delete, name="time_entry_delete"),
]
