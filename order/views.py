from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from admin_pa.models import Category
from cart.models import Cart
from cart.views import clear_applied_coupon
from order.utils import get_current_datetime
from .models import Address, Order, OrderItem
from django.shortcuts import render, redirect
from .forms import AddressForm
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from cart.models import *
from django.contrib import messages
from decimal import Decimal
from django.db.models import F, Sum
from userprofile.models import Address
import razorpay
from gfg import settings





def add_select(request, address_id=None):
    if address_id:
        address = get_object_or_404(Address, id=address_id)
    else:
        address = None

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address_line1 = request.POST.get('address_line1')
        address_line2 = request.POST.get('address_line2')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        house_no = request.POST.get('house_no')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')

        if address:
            address.first_name = first_name
            address.last_name = last_name
            address.addresss_line1 = address_line1
            address.addresss_line2 = address_line2
            address.email = email
            address.phone_number = phone_number
            address.House_No = house_no
            address.street = street
            address.city = city
            address.state = state
            address.postal_code = postal_code
            address.save()
        else:
            address = Address.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                addresss_line1=address_line1,
                addresss_line2=address_line2,
                email=email,
                phone_number=phone_number,
                House_No=house_no,
                street=street,
                city=city,
                state=state,
                postal_code=postal_code,
            )

        # Set this address as the delivery address
        Address.objects.filter(user=request.user, is_delivery_address=True).update(is_delivery_address=False)
        address.is_delivery_address = True
        address.save()

        return redirect('checkout')

    return render(request, 'order/add_select.html', {'address': address})

def Add_address(request, address_id=None):
    if address_id:
        address = get_object_or_404(Address, id=address_id)
    else:
        address = None

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address_line1 = request.POST.get('address_line1')
        address_line2 = request.POST.get('address_line2')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        house_no = request.POST.get('house_no')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
     

        if address:
            address.first_name = first_name
            address.last_name = last_name
            address.addresss_line1 = address_line1
            address.addresss_line2 = address_line2
            address.email = email
            address.phone_number = phone_number
            address.House_No = house_no
            address.street = street
            address.city = city
            address.state = state
            address.postal_code = postal_code
            address.save()
        else:
            address = Address.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                addresss_line1=address_line1,
                addresss_line2=address_line2,
                email=email,
                phone_number=phone_number,
                House_No=house_no,
                street=street,
                city=city,
                state=state,
                postal_code=postal_code,
             
            )
        Address.objects.filter(user=request.user, is_delivery_address=True).update(is_delivery_address=False)
        address.is_delivery_address = True
        address.save()

        return redirect('checkout')

    return render(request, 'order/add_ad.html', {'address': address})





def initiate_payment(request):
    
    if request.method == 'POST':
        # Retrieve the total price and other details from the backend
        cart = Cart.objects.get(user_id=request.user)
        cart_items = cart.cartitems_set.all()

        total_price_str = request.session.get('price_total', '0.00')
        total_price = Decimal(total_price_str)

        total_amount_in_cents = int(total_price*100)
        applied_coupon = request.session.get('applied_coupon', None)
       

        client = razorpay.Client(auth=('rzp_test_gOdh7gSjIuO3AC','M5ZJAeOvlsqplNx5FPogFeHf'))
        




        payment = client.order.create({

            'amount': total_amount_in_cents,
            'currency': 'INR',
            'payment_capture': 1

        })

        response_data = {
            'order_id': payment['id'],
            'amount': payment['amount'],
            'currency': payment['currency'],
            'key': 'rzp_test_gOdh7gSjIuO3AC',

        }
        return JsonResponse(response_data)

    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Invalid request method'})





def choose_delivery_address(request, address_id):
    print("Address ID received:", address_id)
    address = get_object_or_404(Address, id=address_id)

    # Clear any previously selected delivery address
    Address.objects.filter(is_delivery_address=True).update(is_delivery_address=False)

    # Mark the selected address as the delivery address
    address.is_delivery_address = True
    address.save()
    # Redirect back to the checkout page with the selected address ID as a parameter
    return redirect('checkout')




# Create your views here.



def online_payment_order(request, add_id):
   # Initialize the context dictionary

    if request.method == 'POST':
        payment_id = request.POST.getlist('payment_id')[0]
        orderId = request.POST.getlist('orderId')[0]
        signature = request.POST.getlist('signature')[0]
        user_address = get_object_or_404(Address, id=add_id, user=request.user)
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cartitems_set.all()

        total_price = request.session.get('price_total', Decimal('0.00'))

        order = Order.objects.create(
            user=request.user,
            address=user_address,
            total_price=total_price,
            payment_status='ORDERED',
            payment_method='razorpay',  # Change this to 'ONLINE' to distinguish from cash on delivery
            razor_pay_payment_id=payment_id,
            razor_pay_payment_signature=signature,
            razor_pay_order_id=orderId,
        )

        for cart_item in cart_items:
            # Retrieve the discounted price from the session for each product
            price = request.session.get('discounted_price', Decimal('0.00'))
            
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                price=cart_item.price,
                quantity=cart_item.quantity,
            )

            variant = cart_item.product
            variant.stock -= cart_item.quantity
            variant.save()

        cart_items.delete()
        orderId = order.id

        # Clear the applied coupon from the cart after placing the order
        cart.applied_coupon = None
        cart.save()

        return render(request, 'order/order_confirmation.html', )

    # Always render the template, even if the request method is not POST

def order_confirmation(request):
    # Get the order ID and address ID from the query parameters
  

    return render(request, 'order/order_confirmation.html')





def place_order(request, selected_address_id):
    user_address = get_object_or_404(Address, id=selected_address_id, user=request.user)
    cart = Cart.objects.get(user_id=request.user)
    cart_items = cart.cartitems_set.all()
    total_price = request.session.get('price_total', Decimal('0.00'))

    # Check if a delivery address is selected
    if not user_address:
        # Redirect to the checkout view with an error message indicating that no delivery address is selected
        return redirect('checkout_page')

    order = Order.objects.create(
        user=request.user,
        address=user_address,
        total_price=total_price,
        payment_status='ORDERED',
        payment_method='CASH_ON_DELIVERY',  
          
    )
    
    
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            price= cart_item.price,
            quantity=cart_item.quantity
        )

        variant = cart_item.product
        variant.stock -= cart_item.quantity
        variant.save()

    cart_items.delete()

    # Clear the applied coupon from the cart after placing the order
    cart.applied_coupon = None
    
    cart.save()


    # Pass the order and address details in the context
    context = {
        'order': order,
        'address': user_address,
        'order_items': OrderItem.objects.filter(order=order),

    }

    return render(request, 'order/order_confirmation.html', context)



def place_order_with_wallet(request, selected_address_id):
    user = request.user
    user_address = get_object_or_404(Address, id=selected_address_id, user=user)
    cart = Cart.objects.get(user_id=user.id)
    cart_items = cart.cartitems_set.all()
    total_price = request.session.get('price_total', Decimal('0.00'))
    user_wallet = Wallet.objects.get(user=user)

    # Convert total_price to a decimal.Decimal object (if needed)
    total_price = Decimal(total_price)

    # if not user_address:
    #     return redirect('checkout_page')

    # Check if the user's wallet balance is sufficient for the order
    if user_wallet.balance < total_price:
        # Redirect with an error message indicating insufficient balance
        return redirect('checkout_page')  # Modify this to your appropriate URL

    # Create the order and deduct the amount from the wallet balance
    order = Order.objects.create(
        user=user,
        address=user_address,
        total_price=total_price,
        payment_status='ORDERED',
        payment_method='WALLET',  # Indicate payment method as 'WALLET'
    )

    # Deduct the amount from the wallet balance
    user_wallet.balance -= total_price
    user_wallet.save()

    # Create order items and update variant stock
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            price= cart_item.price,
            quantity=cart_item.quantity
       )

        variant = cart_item.product
        variant.stock -= cart_item.quantity
        variant.save()
        
    cart_items.delete()

    # Clear the applied coupon from the cart after placing the order
    cart.applied_coupon = None
    cart.save()

    context = {
        'order': order,
        'address': user_address,
        'order_items': OrderItem.objects.filter(order=order),
    }

    return render(request, 'order/order_confirmation.html', context)



