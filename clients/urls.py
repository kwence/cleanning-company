from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.client_list, name="client_list"),
    path("new/", views.client_form_view, name="client_create"),
    path("<int:pk>/edit/", views.client_form_view, name="client_edit"),
    path("<int:pk>/delete/", views.client_delete, name="client_delete"),
]
