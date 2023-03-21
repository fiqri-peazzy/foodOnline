from django.shortcuts import render,get_object_or_404
from vendor.models import Vendor
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from django.http import HttpResponse,JsonResponse
from .models import Cart
from .context_processor import get_cart_counter,get_cart_amount

from django.contrib.auth.decorators import login_required

# Create your views here.
def marketplace(request):
    vendor = Vendor.objects.filter(is_approved=True, user__is_active=True).order_by('-created_at')
    vendor_count = vendor.count()
    context = {
        'vendors':vendor,
        'vendors_count': vendor_count,
    }
    return render(request, 'marketplace/listing.html', context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    ctx = {
        'vendor':vendor,
        'categories': categories,
        'cart_items':cart_items,
    }
    return render(request, 'marketplace/vendor_detail.html',ctx)

# ajax request
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # if the user has already added that food the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, food_item=fooditem)
                    # increase th cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status':'Success','message':'Increase cart quantity','cart_counter': get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amount(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, food_item=fooditem,quantity=1)
                    return JsonResponse({'status':'Success','message':'added the food','cart_counter': get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amount(request)})

            except:
                return JsonResponse({'status' : 'Failed','message':'This food doesnt exist'})
        else:
            return JsonResponse({'status':'Failed','message':'Invalid Request'})
    else:
        return JsonResponse({'status':'login_required','message':'Please Login to continue'})


def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # if the user has already added that food the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, food_item=fooditem)
                    if chkCart.quantity > 1:

                    # decrease the cart quantity
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({'status':'Success','cart_counter': get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amount(request)})
                except:
                    return JsonResponse({'status':'Failed','message':'You do not have this item in your cart'})

            except:
                return JsonResponse({'status' : 'Failed','message':'This food doesnt exist'})
        else:
            return JsonResponse({'status':'Failed','message':'Invalid Request'})
    else:
        return JsonResponse({'status':'login_required','message':'Please Login to continue'})

@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')

    ctx = {
        'cart_items':cart_items,
    }
    return render(request, 'marketplace/cart.html',ctx)

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            try:
                # chek if the cart item exist
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'Succes','message':'Cart item Has been deleted','cart_counter': get_cart_counter(request),'cart_amount':get_cart_amount(request)})
            except:
                return JsonResponse({'status' : 'Failed','message':'This food doesnt exist'})
        else:
            return JsonResponse({'status':'Failed','message':'Invalid Request'})
