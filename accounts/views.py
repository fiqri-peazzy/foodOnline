from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse

from .models import User, UserProfile
from .forms import UserForm
from vendor.forms import VendorForm

from django.contrib import messages


# Create your views here.
def register_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # create the user by the form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name,username=username,email=email,password=password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'User has been created')
            return redirect('register_user')
        else:
            messages.error(request, 'Sorry, Please try again later')
            print(form.errors)
    else:
        form = UserForm()
    ctx = {
        'form': form,
    }
    return render(request, 'accounts/register_user.html',ctx)

def register_vendor(request):
    if request.method == 'POST':
        # store the data and create user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name,username=username,email=email,password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request, 'Your Account Has been created! please wait for the approval')
            return redirect('register_vendor')
        else:
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()
    ctx ={
        'form':form,
        'v_form':v_form,
    }

    return render(request, 'accounts/register_vendor.html',ctx)
