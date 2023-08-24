from decimal import Decimal
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItems
from .models import *
from .models import WishlistItem
# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from .models import ProductVariant, Wishlist
from django.contrib import messages


@login_required(login_url='signin')
def add_to_wishlist(request, variant_id):
    if request.method == 'POST':
        variant = get_object_or_404(ProductVariant, id=variant_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        # Check if the item already exists in the wishlist
        item = wishlist.wishlistitem_set.filter(product=variant).first()

        if not item:
            # If the item doesn't exist, create a new WishlistItem and save it
            item = WishlistItem(wishlist=wishlist, product=variant)
            item.save()
            messages.success(request, 'Item added to wishlist.')

    return redirect('product_detail', product_id=variant.product.id)

@login_required(login_url='signin')
def wishlist(request):
    user_cart, created = Wishlist.objects.get_or_create(user=request.user)
    items = WishlistItem.objects.filter(wishlist=user_cart).order_by('id')
    
    
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
        item.discounted_price = discounted_price 
    # carts=  CartItems.objects.filter(cart=user_cart)
    context = {
        'items': items,
        #  'carts': items,
    }
    return render(request, 'wishlist/wishlist.html', context)




def wremove(request, item_id):
    if request.method == 'POST':
        try:
            item =  WishlistItem.objects.get(pk=item_id)
            item.delete()
        except  WishlistItem.DoesNotExist:
            pass  
    return redirect('wishlist')
def wishlist_to_cart(request, variant_id):
    if request.method == 'POST':
        variant = get_object_or_404(ProductVariant, id=variant_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        item = cart.cartitems_set.filter(product=variant).first()
        if item:
            item.quantity += 1
            item.save()
            # messages.success(request, 'Item added to cart.')
        else:
            CartItems.objects.create(cart=cart, product=variant, quantity=1, price=variant.sale_price)
            # messages.success(request, 'Item added to cart.')
        
        # Delete the item from the wishlist
        wishlist_item = WishlistItem.objects.filter(product=variant, wishlist__user=request.user)
        if wishlist_item.exists():
            wishlist_item.delete()
            
        return redirect('wishlist')
