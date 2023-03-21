from django.shortcuts import render
from vendor.models import Vendor

def home(request):
    vendor = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    ctx = {
        'vendors':vendor,
    }
    return render(request, 'home.html', ctx)