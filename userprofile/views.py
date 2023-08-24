from decimal import Decimal
from django.shortcuts import redirect, render
from django.shortcuts import render
from authentication.models import UserProfile
from order.models import Order, OrderItem
from userprofile.forms import OrderStatusUpdateForm
from .models import Address, Referral, Wallet
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import Address
from django.shortcuts import render, redirect
from .models import Address
from django.http import HttpResponse, HttpResponseNotAllowed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required(login_url='signin')
def update_profile(request):
    if request.method == 'POST':
        # Get the submitted form data
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        username = request.POST.get('username')
        email = request.POST.get('email')
      
        # Update the user object with the new information
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.save()

        # Add a success message
        messages.success(request, 'Profile successfully updated!')

        # Redirect back to the user profile page or any other desired page
        return redirect('profile')

    return render(request, 'profile/profile.html')



def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'profile/addresslist.html', {'addresses': addresses})



def address_add(request, address_id=None):
  if not User:
      return redirect('signin')
  
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

        return redirect('address_list')

  return render(request, 'profile/addressform.html', {'address': address})

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        # Verify the current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Invalid current password. Please try again.')
            return redirect('change_password')

        # Check if the new password and confirm password match
        if new_password != confirm_new_password:
            messages.error(request, 'New password and confirm password do not match.')
            return redirect('change_password')

        # Update the password
        request.user.password = make_password(new_password)
        request.user.save()

        # Update the session authentication hash to keep the user logged in
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Your password was successfully updated!')
        return redirect('change_password')

    return render(request, 'profile/change_password.html')




def logout_view(request):
    logout(request)
    return redirect('interface') 






@login_required
def order_list(request):
    if request.user.is_superuser:
        # For superusers, fetch all orders
        orders = Order.objects.all()
    else:
        # For regular users, fetch their own orders
        orders = Order.objects.filter(user=request.user)

    # Pagination
    page = request.GET.get('page')
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    if request.user.is_superuser:
        return render(request, 'profile/admin.html', {'orders': orders})
    else:
        return render(request, 'profile/orderlist.html', {'orders': orders})



def adorder_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    ordered_products = []
    total_price = Decimal('0.00')

    for order_item in order_items:
        product_variant = order_item.product # Use the Decimal version of the price
        quantity = Decimal(order_item.quantity)
        discounted_price = Decimal(order_item.price) 
        total_price = discounted_price * quantity
        ordered_product = {
            'name': product_variant.product.name,
            'size': str(product_variant.size),  # Use Decimal price here
            'quantity': quantity,
            'images': product_variant.images.all(),
            'price': discounted_price,
        }
        ordered_products.append(ordered_product)

          

    form = OrderStatusUpdateForm(request.POST or None, instance=order)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('adorder_details', order_id=order_id)

    context = {
        'order': order,
        'ordered_products': ordered_products,
        'address': order.address,
        'total_price': total_price,  # Include the total price in the context
        'form': form,
    }

    return render(request, 'profile/admin_views.html', context)






def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    ordered_products = []
    total_price = Decimal('0.00')  # Initialize total price to Decimal
      # Initialize discounted price to Decimal
    
    for order_item in order_items:
        product_variant = order_item.product # Use the Decimal version of the price
        quantity = Decimal(order_item.quantity)
        product_price = Decimal(order_item.price)
        total_price =   product_price * quantity
        ordered_product = {
            'name': product_variant.product.name,
            'size': str(product_variant.size),
            'quantity': quantity,
            'images': product_variant.images.all(),
            'subtotal': product_price * quantity,
            'product_price':product_price,
        }
        ordered_products.append(ordered_product)
        
          
    context = {
        'order': order,
        'ordered_products': ordered_products,
        'address': order.address,
        'total_price': total_price,
    }

    return render(request, 'profile/ordersview.html', context)




def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.payment_status == 'CANCELLED':
        # Handle already cancelled order
        pass
    else:
        try:
            user_wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            # Handle the case where the wallet does not exist for the user
            pass
        else:
            if order.payment_method != 'CASH_ON_DELIVERY':
                refund_amount = Decimal('0.0')

                for order_item in OrderItem.objects.filter(order=order):
                    product_variant = order_item.product
                    product_variant.stock += order_item.quantity
                    product_variant.save()

                    refund_amount += Decimal(order_item.price) * order_item.quantity

                user_wallet.balance += refund_amount
                user_wallet.save()

            # Update order status to 'CANCELLED' regardless of payment method
            order.payment_status = 'CANCELLED'
            order.save()

    return redirect('order_details', order_id=order.id)


              
@login_required
def show_wallet(request):
    user = request.user
    
    wallet = Wallet.objects.get(user=user)  # Retrieve the user's wallet
    context = {'wallet': wallet}
    return render(request, 'profile/wallet.html', context)
User = get_user_model()




@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)



@login_required(login_url='signin')  # Assuming you want to show the referral code only to logged-in users
def profile(request):
    user = request.user
    referral_code = None
    
    # Retrieve the referral code if the user has referrals
    if hasattr(user, 'referrals_made'):
        referral_code = user.referrals_made.first().referral_code
    
    return render(request, "profile/profile.html", {'referral_code': referral_code})



def user_profile(request):
    user = request.user  # Assuming the user is logged in
    profile = UserProfile.objects.get(user=user)  # Fetch the user's profile

    referred_user = None
    referring_user = None

    if profile.referral_code:
        try:
            referral = Referral.objects.get(referral_code=profile.referral_code)
            referred_user = referral.referred_user
            referring_user = referral.referring_user
        except Referral.DoesNotExist:
            referred_user = None

    context = {
        'user': user,
        'profile': profile,
        'referred_user': referred_user,
        'referring_user': referring_user,
    }

    return render(request, "authentication/user_profile.html", context)




