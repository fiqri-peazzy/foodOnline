from django.shortcuts import render, redirect
from marketplace.models import Cart
from django.contrib.auth.decorators import login_required
from marketplace.context_processor import get_cart_amount
from .forms import OrderForm
from .models import Order, Payment, OrderedFood
from .utils import generate_order_number,order_total_by_vendor
from django.http import HttpResponse,JsonResponse
import midtransclient
import simplejson as json
from foodonline_main.settings import SERVER_KEY_MIDTRANS
from menu.models import FoodItem
from marketplace.models import Tax
from django.contrib.sites.shortcuts import get_current_site
from accounts.utils import send_notification_email

# Create your views here.

@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')

    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    vendors_ids = []
    for i in cart_items:
        if i.food_item.vendor.id not in vendors_ids:
            vendors_ids.append(i.food_item.vendor.id)


    
    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    total_data = {}
    k = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.food_item.id, vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (fooditem.price * i.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (fooditem.price * i.quantity)
            k[v_id] = subtotal

        # Calculate The tax_data
        tax_dict = {}

        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100,2)
            tax_dict.update({tax_type: {str(tax_percentage) : str(tax_amount)}})
        
        total_data.update({fooditem.vendor.id: {str(subtotal) : str(tax_dict)}})
    

    subtotal = get_cart_amount(request)['subtotal']
    total_tax = get_cart_amount(request)['tax']
    grand_total = get_cart_amount(request)['grand_total']
    tax_data = get_cart_amount(request)['tax_dict']

    if request.method == "POST":
        form = OrderForm(request.POST)

        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_mthod = request.POST['payment-method']
            
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()

            # Midtrans Payment Gateway
            snap = midtransclient.Snap(
                # Set to true if you want Production Environment (accept real transaction).
                is_production=False,
                server_key=SERVER_KEY_MIDTRANS,
            )
            # Create Snap API instance
            
            total_idr = subtotal * 14950
            # Build API parameter
            
            for item in cart_items:
                param = {
                    "transaction_details": {
                        "order_id": order.order_number,
                        "gross_amount": int(total_idr)
                    }, "credit_card":{
                        "secure" : True
                    },
                    "customer_details":{
                        "first_name": order.first_name,
                        "last_name": order.last_name,
                        "email": order.email,
                        "phone": order.phone
                    }
                }

            transaction = snap.create_transaction(param)

            transaction_token = transaction['token']

            ctx = {
                'order': order,
                'cart_items': cart_items,
                'transaction_token':transaction_token
            }
            return render(request, 'orders/place_order.html', ctx)
            print(form.errors)
    return render(request, 'orders/place_order.html')

@login_required(login_url='login')
def payments(request):

        # Check if the request is ajax or not
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'POST':
        # store the payment details in the payment models
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(user=request.user, order_number=order_number)

        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount = order.total,
            status = status
        )

        payment.save()
        # update the order model
        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.food_item
            ordered_food.quantity = item.quantity
            ordered_food.price = item.food_item.price
            ordered_food.amount = item.food_item.price * item.quantity
            ordered_food.save()

        # Send Order COnfirmation Email to customer
        mail_subject = 'Thank You for ordering with us'
        mail_template = 'orders/order_confirm_email.html'
        ordered_food = OrderedFood.objects.filter(order=order)
        customer_subtotal = 0
        for item in ordered_food:
            customer_subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)
        context = {
            'user':request.user,
            'order':order,
            'to_email':order.email,
            'ordered_food':ordered_food,
            'domain':get_current_site(request),
            'customer_subtotal':customer_subtotal,
            'tax_data':tax_data,

        }
        send_notification_email(mail_subject, mail_template, context)

        # Send Order Confirmation Email to Vendor
        mail_subject = 'you have received a new order'
        mail_template = 'orders/new_order_received.html'
        to_emails = []
        for i in cart_items:
            if i.food_item.vendor.user.email not in to_emails:
                to_emails.append(i.food_item.vendor.user.email)
                ordered_food_to_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor=i.food_item.vendor)

                context = {
                    'order':order,
                    'to_email':i.food_item.vendor.user.email,
                    'ordered_food_to_vendor':ordered_food_to_vendor,
                    'vendor_subtotal':order_total_by_vendor(order, i.food_item.vendor.id)['subtotal'],
                    'tax_data':order_total_by_vendor(order, i.food_item.vendor.id)['tax_dict'],
                    'vendor_grand_total':order_total_by_vendor(order, i.food_item.vendor.id)['grand_total'],
                }
                send_notification_email(mail_subject, mail_template, context)

        cart_items.delete()
        response = {
            'order_number':order_number,
            'transaction_id':transaction_id
        }
        return JsonResponse(response)

    return HttpResponse('Payment View')

def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)
        ctx = {
            'order':order,
            'ordered_food':ordered_food,
            'subtotal':subtotal,
            'tax_data':tax_data,
        }
        return render(request, 'orders/order_complete.html',ctx)
    except:
        return redirect('home')

    