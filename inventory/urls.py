"""
URL configuration for inventory app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('items/', views.item_list, name='item_list'),
    path('items/<str:item_id>/', views.item_detail, name='item_detail'),
]
