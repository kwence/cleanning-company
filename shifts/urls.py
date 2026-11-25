from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.shift_list, name="shift_list"),
    path("new/", views.shift_create, name="shift_create"),
    path("<int:pk>/edit/", views.shift_edit, name="shift_edit"),
    path("<int:pk>/delete/", views.shift_delete, name="shift_delete"),
    path("<int:pk>/complete/", views.shift_complete, name="shift_complete"),
]
