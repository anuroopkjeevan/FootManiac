from decimal import Decimal
from itertools import product
from django import template
from django.core.paginator import Paginator
import logging
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from admin_pa.models import Category, Offer, Product, ProductVariant
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
import random
import string
from datetime import date, datetime, timedelta, timezone
from authentication.models import UserProfile
from cart.models import CartItems
import userprofile
from django.utils import timezone
from django.db.models import Q
from admin_pa .models import size
from userprofile.models import Referral
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import MultipleObjectsReturned
from django.utils.encoding import force_bytes
from django.db import transaction
from userprofile.models import  Wallet
from django.db.models import Q, Sum
from django.utils import timezone
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
 # Import your models here

def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)  # Define month_ago here

    # Query for top selling products for the month
    top_selling_products_month = CartItems.objects.filter(cart__created_at__range=[month_ago, today]).values('product__model_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]

    # Prepare the context dictionary with the queried categories, products, and top selling products
    context = {
        'Categories': categories,
        'products': products,
        'top_selling_products_month': top_selling_products_month,  # Include this in the context
    }
    return render(request, "authentication/index.html", context)

#LANDING PAGE


#EMAIL_CONFIRMATIO
def home_2(request):
    return render(request, "authentication/home.html")  



def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_panel')
             
            else: 
              return redirect('home')
          
         
            
        else:            
            pass    

    return render(request, "authentication/signin.html")
def signup(request):
    if request.method == "POST":
        # Extract user registration data from the form
        username = request.POST.get('username')
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        email = request.POST.get('email')
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('confirm_password')
        referral_code = request.POST.get('referral_code')  # Add this line to extract referral code

        # Create the user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        # Check and create referral relationship
        referrer = None
        try:
            referrer = User.objects.get(referrals_made__referral_code=referral_code)
        except User.DoesNotExist:
            # Handle invalid referral codes here
            pass
        except MultipleObjectsReturned:
            print(f"Multiple users found with referral code: {referral_code}")
            # Handle this case or log an error message

        # Add 50 Rs to both the referred user's and referral owner's wallets
        if referrer:
            with transaction.atomic():
                referrer_wallet = Wallet.objects.get(user=referrer)
                referred_wallet = Wallet.objects.get(user=myuser)
        
                referrer_wallet.balance += Decimal('50.00')
                referred_wallet.balance += Decimal('50.00')

                referrer_wallet.save()
                referred_wallet.save()

        # Welcome email
        subject = "Welcome to foot_maniac"
        message = f"Hello {myuser.first_name}, thank you for visiting our website. We have sent a confirmation email to your email address. Please confirm your email in order to activate your account."
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Address confirmation Email
        current_site = 'http://16.171.10.193/'
        email_subject = "Confirm Email @ GFG - Django Login!!"
        uidb64 = urlsafe_base64_encode(force_bytes(myuser.pk))
        token = default_token_generator.make_token(myuser)
        message2 = render_to_string('email_confirmation.html', {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uidb64': uidb64,
            'token': token,
        })

        email = EmailMessage(
            email_subject,
            message2,
            from_email,
            [myuser.email],
        )
        email.send()

        return redirect('home_2')

    return render(request, "authentication/signup.html")



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and default_token_generator.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        messages.success(request, 'Your account has been activated successfully.')
        return redirect('signin')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('signup')

def check_email_view(request):
    return render(request, "authentication/check_email.html")

  

def women(request):
    # Assuming category with id=1 corresponds to women's category
    womens_category = Category.objects.get(name='women')

    products = Product.objects.filter(category=womens_category)
    random_variants = []

    # Get selected filter values
    selected_price_range = request.GET.get('price_range')
    selected_size = request.GET.get('size_width')

    # Convert the selected_price_range to min and max price values
    min_price_range, max_price_range = None, None
    if selected_price_range:
        if selected_price_range == '0-1000':
            max_price_range = 1000
        elif selected_price_range == '0-2000':
            max_price_range = 2000
        elif selected_price_range == '0-4000':
            max_price_range = 4000

    for product in products:
        # Get all variants for the current product
        variants = ProductVariant.objects.filter(product=product, is_active=True)

        if variants.exists():
            # Apply filters to the variants
            if selected_size:
                variants = variants.filter(size__size=selected_size)

            # Filter variants by price range
            if min_price_range is not None:
                variants = variants.filter(sale_price__gt=min_price_range)
            if max_price_range is not None:
                variants = variants.filter(sale_price__lte=max_price_range)

            if variants.exists():
                # Select a random variant from the filtered variants
                random_variant = random.choice(variants)

                # Calculate the discounted price based on the higher discount percentage (variant or category)
                original_price = random_variant.sale_price
                variant_discount_percentage = random_variant.discount_percentage
                category_discount_percentage = 0  # Initialize category discount percentage

                try:
                    category_discount = Offer.objects.get(category=womens_category)
                    category_discount_percentage = category_discount.discount_percentage
                except Offer.DoesNotExist:
                    pass

                max_discount_percentage = max(variant_discount_percentage, category_discount_percentage)
                discounted_price = original_price - (original_price * Decimal(max_discount_percentage / 100))

                # Add the discounted price and discount percentage to the random variant
                random_variant.discounted_price = discounted_price
                random_variant.greatest_discount_percentage = max_discount_percentage

                # Add the random variant to the list
                random_variants.append((product, random_variant))

    # Get all available sizes from the database
    available_sizes = size.objects.all()

    # Pagination
    items_per_page = 6
    paginator = Paginator(random_variants, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'min_price_range': min_price_range,
        'max_price_range': max_price_range,
        'size_width': selected_size,
        'available_sizes': available_sizes,
    }
    
    return render(request, 'authentication/women.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    selected_size = request.POST.get('selected_size')

    if selected_size:
        variant = get_object_or_404(ProductVariant, id=selected_size)
    else:
        variant = product.productvariant.first()

    product_variants = product.productvariant.all()

    # Get the variant discount percentage
    variant_discount_percentage = variant.discount_percentage if variant else None
    

    # Calculate category discount percentage
    category_discount_percentage = 0
    try:
        category_discount = Offer.objects.get(category=product.category)
        category_discount_percentage = category_discount.discount_percentage
   
    except Offer.DoesNotExist:
        pass

    # Calculate the discounted price based on the higher discount percentage (variant or category)
    original_price = variant.sale_price if variant else product.price
    if variant_discount_percentage is not None and category_discount_percentage is not None:
        max_discount_percentage = max(variant_discount_percentage, category_discount_percentage)
    elif variant_discount_percentage is not None:
        max_discount_percentage = variant_discount_percentage
    elif category_discount_percentage is not None:
        max_discount_percentage = category_discount_percentage
    else:
        max_discount_percentage = 0

    discounted_price = original_price - (original_price * Decimal(max_discount_percentage / 100))

    context = {
        'product': product,
        'variant': variant,
        'product_variants': product_variants,
        'discounted_price': discounted_price,
        'max_discount_percentage': max_discount_percentage,
    }
    
    return render(request, 'authentication/product.html', context)


  
def men(request):

    womens_category = Category.objects.get(name='men')

    products = Product.objects.filter(category=womens_category)
    random_variants = []

    # Get selected filter values
    selected_price_range = request.GET.get('price_range')
    selected_size = request.GET.get('size_width')

    # Convert the selected_price_range to min and max price values
    min_price_range, max_price_range = None, None
    if selected_price_range:
        if selected_price_range == '0-1000':
            max_price_range = 1000
        elif selected_price_range == '0-2000':
            max_price_range = 2000
        elif selected_price_range == '0-4000':
            max_price_range = 4000

    for product in products:
        # Get all variants for the current product
        variants = ProductVariant.objects.filter(product=product, is_active=True)

        if variants.exists():
            # Apply filters to the variants
            if selected_size:
                variants = variants.filter(size__size=selected_size)

            # Filter variants by price range
            if min_price_range is not None:
                variants = variants.filter(sale_price__gt=min_price_range)
            if max_price_range is not None:
                variants = variants.filter(sale_price__lte=max_price_range)

            if variants.exists():
                # Select a random variant from the filtered variants
                random_variant = random.choice(variants)

                # Calculate the discounted price based on the higher discount percentage (variant or category)
                original_price = random_variant.sale_price
                variant_discount_percentage = random_variant.discount_percentage
                category_discount_percentage = 0  # Initialize category discount percentage

                try:
                    category_discount = Offer.objects.get(category=womens_category)
                    category_discount_percentage = category_discount.discount_percentage
                except Offer.DoesNotExist:
                    pass

                max_discount_percentage = max(variant_discount_percentage, category_discount_percentage)
                discounted_price = original_price - (original_price * Decimal(max_discount_percentage / 100))

                # Add the discounted price and discount percentage to the random variant
                random_variant.discounted_price = discounted_price
                random_variant.greatest_discount_percentage = max_discount_percentage

                # Add the random variant to the list
                random_variants.append((product, random_variant))

    # Get all available sizes from the database
    available_sizes = size.objects.all()

    # Pagination
    items_per_page = 6
    paginator = Paginator(random_variants, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'min_price_range': min_price_range,
        'max_price_range': max_price_range,
        'size_width': selected_size,
        'available_sizes': available_sizes,
    }
  
    return render(request, 'authentication/men.html', context)


def interface(request):
    # Fetch all Category objects from the database
    categories = Category.objects.all()

    # Prepare the context dictionary with the queried categories
    context = {
        'Categories': categories
    }

    # Render the template 'women.html' with the context data
    return render(request, 'authentication/interface.html', context)




def Direct(request,category_id):
    if category_id== 3:
        return redirect('men')
    else:
        return redirect('women')
    
    
    
    
# views.py

# Helper function to generate OTP
# views.py


# Helper function to generate OTP
def generate_otp():
    # Generate a 6-digit random OTP
    return str(random.randint(100000, 999999))



def password_reset_request(request):
    error_message = None  # Initialize error message to None

    if request.method == 'POST':
        email = request.POST.get('email')

        # Validate email format
        if not email:
            return HttpResponseBadRequest("Invalid email address")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            error_message = 'Invalid email address'  # Set the error message

        if not error_message:
            user_profile, created = UserProfile.objects.get_or_create(user=user)

            otp = generate_otp()
            user_profile.otp = otp
            user_profile.otp_expiry = datetime.now() + timedelta(minutes=10)
            user_profile.save()

            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}',
                'noreply@example.com',  # Use a proper noreply email address
                [email],
                fail_silently=False,
            )
            return redirect('verify_otp')  # You need to have this endpoint defined

    return render(request, 'password_reset/password_reset_request.html', {'error_message': error_message})


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        try:
            print( otp)
            userprofile = UserProfile.objects.get(otp=otp, otp_expiry__gte=timezone.now())
        except UserProfile.DoesNotExist:
            return render(request, 'password_reset/verify_otp.html', {'error_message': 'Invalid OTP'})

        # Store the userprofile in the session to use it in the reset_password view
        request.session['userprofile_id'] = userprofile.id

        return redirect('reset_password')
    return render(request, 'password_reset/verify_otp.html')



def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']

        # Retrieve the userprofile from the session
        userprofile_id = request.session.get('userprofile_id')
        if userprofile_id is None:
            # Redirect to the verify_otp view if the userprofile is not found in the session
            return redirect('verify_otp')

        try:
            userprofile = UserProfile.objects.get(pk=userprofile_id)
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found.')
            
            return redirect('verify_otp')

        # Get the associated user from the userprofile
        user = userprofile.user

        # Update the user's password with the new one
        user.set_password(password)
        user.save()

        # Clear the userprofile from the session after successful password reset
        del request.session['userprofile_id']

        return redirect('signin')  # Redirect to the login page or any other page

    return render(request, 'password_reset/resetpassword.html')



# In your view or context processor
