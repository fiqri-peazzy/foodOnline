from django import views
from django.urls import path
from . import views


urlpatterns = [
    path('register_user/',views.register_user, name='register_user'),
    path('register_vendor/',views.register_vendor, name='register_vendor'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('my_account/',views.my_account, name='my_account'),
    path('customer_dahsboard/', views.cust_dashboard, name='custDashboard'),
    path('vendor_dahsboard/', views.vend_dashboard, name='vendorDashboard'),
]