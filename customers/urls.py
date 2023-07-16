from django.urls import path
from accounts import views as AccountViews
from . import views

urlpatterns = [
    path('', AccountViews.cust_dashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
    path('my_orders/',views.my_orders, name='cust_my_orders'),
    path('order_details/<int:order_number>/', views.order_details, name='order_details'),
]