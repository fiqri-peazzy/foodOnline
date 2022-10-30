from django import views
from django.urls import path
from . import views


urlpatterns = [
    path('register_user/',views.register_user, name='register_user'),
    path('register_vendor/',views.register_vendor, name='register_vendor'),
]