import datetime
from django.db.models import F
from django.contrib import messages
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import redirect, render
from admin_pa.models import Category, Offer, Product, ProductVariant
from cart.forms import CouponForm
# from cart.forms import CouponForm, ShippingAddressForm
from cart.models import Cart, CartItems, Coupon
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from order.models import Order
from  userprofile.models import Address
from django.contrib import messages
from django.contrib.auth.models import User


@login_required(login_url='signin')
def add_to_cart(request, variant_id):
    if request.method == 'POST':
        variant = get_object_or_404(ProductVariant, id=variant_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        item = cart.cartitems_set.filter(product=variant).first()
        if item:
            item.quantity += 1
            item.save()
            messages.success(request, 'Item added to cart.')
        else:
            CartItems.objects.create(cart=cart, product=variant, quantity=1, price=variant.sale_price)
            messages.success(request, 'Item added to cart.')
            
        return redirect('product_detail', product_id=variant.product.id)





@login_required(login_url='signin')
def cart(request):

    user_cart, created = Cart.objects.get_or_create(user=request.user)

    items = CartItems.objects.filter(cart=user_cart).order_by('id')

    total_discounted_amount = 0  # Initialize total discounted amount
    total_original_price = 0  # Initialize total original price

    for item in items:
        # Calculate the discounted price for each item based on variant or category discount
        variant_discount_percentage = item.product.discount_percentage
        category_discount_percentage = 0
                    
        try:
            category_discount = Offer.objects.get(category=item.product.product.category)
            category_discount_percentage = category_discount.discount_percentage
        except Offer.DoesNotExist:
            pass

        original_price = item.product.sale_price
        if variant_discount_percentage is not None and category_discount_percentage is not None:
            max_discount_percentage = max(variant_discount_percentage, category_discount_percentage)
        elif variant_discount_percentage is not None:
            max_discount_percentage = variant_discount_percentage
        elif category_discount_percentage is not None:
            max_discount_percentage = category_discount_percentage
        else:
            max_discount_percentage = 0

        discounted_price = original_price - (original_price * Decimal(max_discount_percentage / 100))
        item.price= discounted_price 
        item.save()# Update the item's discounted price
        total_discounted_amount += (original_price - discounted_price) * item.quantity
        total_original_price += original_price * item.quantity
        

    

    total_price = total_original_price - total_discounted_amount

    applied_coupon = user_cart.applied_coupon
    discount_amount = applied_coupon.value if applied_coupon else 0

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'apply_coupon':
            coupon_code = request.POST.get('coupon_code')
            try:
                applied_coupon = Coupon.objects.get(code=coupon_code)
                if applied_coupon.valid_from <= timezone.now() <= applied_coupon.valid_to:
                    user_cart.applied_coupon = applied_coupon
                    user_cart.save()
                    messages.success(request, f"Coupon '{coupon_code}' applied successfully!")
                else:
                    messages.error(request, "Coupon is not valid at this time.")
            except Coupon.DoesNotExist:
                messages.error(request, "Invalid coupon code.")
        elif action == 'remove_coupon':
            user_cart.applied_coupon = None
            user_cart.save()
            messages.success(request, "Coupon removed successfully!")

        return redirect("cart")

    # Calculate discounted total price if coupon is not applied
    discounted_total_price = total_price - discount_amount
    # After calculating the discounted_total_price
    Coupons= Coupon.objects.all()
     
    context = {
        'items': items,
        'total_original_price': total_original_price,
        'total_discounted_amount': total_discounted_amount,
        'discounted_total_price': discounted_total_price,
        'applied_coupon': applied_coupon,
        'discount_amount': discount_amount,
        'messages': messages.get_messages(request),
        'Coupons': Coupons,
    }
     
    return render(request, 'cart/cart.html', context)









def checkout(request):
    user = request.user
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        # Handle the case when the user doesn't have a cart
        return redirect('cart')  # Redirect to the cart page or appropriate view

    cart_items = cart.cartitems_set.all()  # Correct way to access related items
    addresses = Address.objects.filter(user=user).order_by("id")
    selected_address = addresses.filter(is_delivery_address=True).first()

    if not selected_address:
        return redirect('add_select')

    out_of_stock_products = [
        f"{item.product.product.name} - {item.product.size}"
        for item in cart_items
        if item.product.stock < item.quantity
    ]

    if out_of_stock_products:
        error_message = ", ".join(out_of_stock_products) + " is out of stock. Please remove them from your cart."
        messages.error(request, error_message)
        return redirect('cart')

    subtotal = Decimal('0')  # Initialize subtotal
    for item in cart_items:
        subtotal += item.get_item_price()  # Calculate the subtotal correctly

    shipping_charge = Decimal('50') if subtotal < Decimal('1000') else Decimal('0.00')

    # Fetch the applied coupon for the user's cart
    applied_coupon = cart.applied_coupon
    discount_amount_coupon = applied_coupon.value if applied_coupon else Decimal('0')

    # Calculate category and variant discounts
    total_category_discount = Decimal('0')
    for item in cart_items:
        variant_discount_percentage = item.product.discount_percentage
        category_discount_percentage = Decimal('0')

        try:
            category_discount = Offer.objects.get(category=item.product.product.category)
            category_discount_percentage = category_discount.discount_percentage
        except Offer.DoesNotExist:
            pass

        if variant_discount_percentage is not None and category_discount_percentage is not None:
            max_discount_percentage = max(variant_discount_percentage, category_discount_percentage)
        elif variant_discount_percentage is not None:
            max_discount_percentage = variant_discount_percentage
        elif category_discount_percentage is not None:
            max_discount_percentage = category_discount_percentage
        else:
            max_discount_percentage = Decimal('0')

        original_price = item.product.sale_price
        discounted_price = original_price - (original_price * Decimal(max_discount_percentage / 100))
        total_category_discount += (original_price - discounted_price) * item.quantity
        request.session['discounted_price'] = str(discounted_price)
    # Calculate total price after applying discounts
    price_total = (subtotal ) + shipping_charge - discount_amount_coupon
    request.session['total_category_discount'] = str(total_category_discount)
    request.session['price_total'] = str(price_total)
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping_charge': shipping_charge,
        'discount_amount_coupon': discount_amount_coupon,
        'total_category_discount': total_category_discount,
        'price_total': price_total,
        'cart_items': cart_items,
        'addresses': addresses,
        'selected_address': selected_address,
        'applied_coupon': applied_coupon,  # Pass the applied coupon
    }

    return render(request, 'cart/checkout.html', context)




def page_empty(request):
    return redirect(request,"templates/cart/empty.html")




def coupon_list(request):
    coupons = Coupon.objects.all()
    context = {
        'coupons': coupons
    }
   
    return render(request, 'cart/coupon_list.html', context)

def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            # You can add a success message here if you're using messages framework
            return redirect('coupon_list')  # Redirect to the coupon list page after adding the coupon
    else:
        form = CouponForm()
    
    context = {
        'form': form,
    }
    return render(request, 'cart/add_coupon.html', context)

def create_coupon(request):
    if request.method == 'POST':
        # Retrieve the data from the request.POST dictionary
        code = request.POST.get('code')
        discount_type = request.POST.get('discount_type')
        value = request.POST.get('value')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        max_usage_limit = request.POST.get('max_usage_limit')
        used_count = request.POST.get('used_count')

        # Create a new Coupon object
        coupon = Coupon.objects.create(
            code=code,
            discount_type=discount_type,
            value=value,
            valid_from=valid_from,
            valid_to=valid_to,
            max_usage_limit=max_usage_limit,
            used_count=used_count,
        )
        coupon.save()
        return redirect('coupon_list')  # Assuming 'coupon_list' is the name of the view for listing coupons.
    # If the request method is not POST, render the 'create_coupon.html' template.
    return render(request, 'cart/create_coupon.html')



def clear_applied_coupon(cart):
    cart.applied_coupon.clear()
    
    
    
def remove_item(request, variant_id):
    if request.method == 'POST':
        try:
            item = CartItems.objects.get(pk=variant_id)
            item.delete()
        except CartItems.DoesNotExist:
            pass  
    return redirect('cart')

# views.py    




def update_cart_item(request, item_id, quantity):
    if request.method == 'GET':
        try:
            item = CartItems.objects.get(pk=item_id)
            
            # Ensure the new quantity is at least 0, and show 0 if the new quantity is less than 1
            new_quantity = max(1, int(quantity))  # Ensure new_quantity is an integer
            
            item.quantity = new_quantity
            item.save()
        except CartItems.DoesNotExist:
            pass
    return redirect('cart')


