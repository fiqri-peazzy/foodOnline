from django.urls import path
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('',AccountViews.vend_dashboard),
    path('profile/',views.v_profile, name='v_profile'),
]