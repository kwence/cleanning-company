from django.urls import path

from . import views

urlpatterns = [
    path("stock/", views.stock_list, name="stock_list"),
    path("stock/new/", views.stock_item_create, name="stock_item_create"),
    path("stock/<int:pk>/edit/", views.stock_item_edit, name="stock_item_edit"),
    path("stock/movements/", views.stock_movements, name="stock_movements"),
    path("stock/orders/", views.stock_orders, name="stock_orders"),
    path("stock/orders/<int:pk>/receive/", views.stock_order_receive, name="stock_order_receive"),
    path("equipment/", views.equipment_list, name="equipment_list"),
    path("equipment/new/", views.equipment_create, name="equipment_create"),
    path("equipment/<int:pk>/edit/", views.equipment_edit, name="equipment_edit"),
]