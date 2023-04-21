from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.get_user),
    path('login/', views.login),
    path('register/', views.register),
    path('order/', views.order),
    path('order/change/', views.change_order),
    path('orders/', views.orders),
]
