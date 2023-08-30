import datetime
import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from pyexpat.errors import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from admin_pa.forms import CategoryForm
from admin_pa.forms import ProductForm
from django.shortcuts import render, redirect
from django.shortcuts import redirect, render, get_object_or_404
from cart.models import CartItems
from .models import Category, Offer, ProductImage
from .models import Product, ProductVariant
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from .forms import ProductImageformsForm, ProductVariantForm, SearchForm
from .models import ProductVariant
import random
from .models import SalesReport
from django.db.models import Sum, Count
from django.utils.timezone import make_aware
from order.models import Order, OrderItem
from django.http import HttpResponseBadRequest
from django.db.models import Q, Sum
from django.utils import timezone
from django.db.models.functions import TruncDate
from datetime import timedelta
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.paginator import Paginator
from decimal import Decimal
from datetime import datetime

def calculate_discount(variant, category=None):
    original_price = variant.sale_price
    variant_discount_percentage = variant.discount_percentage
    category_discount_percentage = 0
    
    if category:
        try:
            category_discount = Offer.objects.get(category=category)
            category_discount_percentage = category_discount.discount_percentage
        except Offer.DoesNotExist:
            pass

    max_discount_percentage = max(variant_discount_percentage, category_discount_percentage)
    discounted_price = original_price - (original_price * Decimal(max_discount_percentage / 100))

    return discounted_price, max_discount_percentage



def search_view(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = ProductVariant.objects.filter(model_name__icontains=query, is_active=True)

    random_variants = []
    for result in results:
        if result.product.is_active:
            discounted_price, max_discount_percentage = calculate_discount(result)
            result.discounted_price = discounted_price
            result.greatest_discount_percentage = max_discount_percentage
            random_variants.append(result)

    items_per_page = 6
    paginator = Paginator(random_variants, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'results': results,
    }
    return render(request, 'search/search.html', context)




def enable(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = True
    print("Product enabled")
    product.save()
    print("Enabled")

    return redirect('product') 



def disable(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = False
    print("Product disabled")
    product.save()
    

    return redirect('product')  # Assuming 'product_list' is a valid URL name for the product list page





def block_user(request,user_id):
    print(user_id)
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    user.is_active = False
    print("user blocked")
    user.save()
    print("block")

    return redirect('dashboard')

def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    print(user)
    user.is_active = True  # Set the user's is_active field to True to unblock the user
    user.save()
    print("unblock")

    return redirect('dashboard')



def dashboard(request):
    users = User.objects.all().order_by('-id')  # Order users by ID in descending order
    
    # Apply search filter if search query is provided
    search_query = request.GET.get('search', '')  # Use an empty string as default
    if search_query:
        users = users.filter(Q(username__icontains=search_query) | Q(email__icontains=search_query))
    
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_users = paginator.get_page(page_number)
    
    context = {
        'page_users': page_users,
        'search_query': search_query
    }

    return render(request, 'authentication/dashboard.html', context)




def admin_panel(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not start_date and not end_date:
            current_date = timezone.now().date()
            default_start_date = current_date - timedelta(days=30)
            default_end_date = current_date
            start_date = default_start_date.strftime('%Y-%m-%d')
            end_date = default_end_date.strftime('%Y-%m-%d')

        if start_date and end_date:
            order_count_date = Order.objects.filter(
                Q(order_date__date__gte=start_date, order_date__date__lte=end_date) |
                Q(order_date__date=end_date, order_date__isnull=True)
            ).exclude(payment_status='CANCELLED').count()

            total_price_date = Order.objects.filter(
                Q(order_date__date__gte=start_date, order_date__date__lte=end_date) |
                Q(order_date__date=end_date, order_date__isnull=True)
            ).exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']

            daily_totals = Order.objects.filter(
                Q(order_date__date__gte=start_date, order_date__date__lte=end_date) |
                Q(order_date__date=end_date, order_date__isnull=True)
            ).exclude(payment_status='CANCELLED').annotate(date=TruncDate('order_date')).values('date').annotate(
                total=Sum('total_price')).order_by('date')

            order_count = Order.objects.exclude(payment_status='CANCELLED').count()
            total_price = Order.objects.exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']
            
            today = timezone.now().date()
            today_orders = Order.objects.filter(order_date__date=today)
            order_count_today = today_orders.count()
            total_price_today = sum(order.total_price for order in today_orders)
            
            recent_orders = Order.objects.order_by('-order_date')[:3]
            
            top_selling_products = OrderItem.objects.values('product__product__name').annotate(
               total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]


            categories = Category.objects.all()
            data = [Product.objects.filter(category=category).count() for category in categories]

            context = {
                'order_count_date': order_count_date,
                'total_price_date': total_price_date,
                'start_date': start_date,
                'end_date': end_date,
                'daily_totals': daily_totals,
                'order_count': order_count,
                'total_price': total_price,
                'categories': categories,
                'data': data,
                'order_count_today': order_count_today,
                'total_price_today': total_price_today,
                'recent_orders': recent_orders,
                'top_selling_products': top_selling_products,
            }

            return render(request, 'authentication/adminpaenl.html', context)

        else:
            order_count = Order.objects.exclude(payment_status='CANCELLED').count()
            total_price = Order.objects.exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']

            today = timezone.now().date()
            today_orders = Order.objects.filter(order_date__date=today)
            order_count_today = today_orders.count()
            total_price_today = sum(order.total_price for order in today_orders)

            categories = Category.objects.all()
            data = [Product.objects.filter(category=category).count() for category in categories]

            recent_orders = Order.objects.order_by('-order_date')[:3]

            top_selling_products = OrderItem.objects.values('product__name').annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')[:5]

            context = {
                'order_count': order_count,
                'total_price': total_price,
                'start_date': start_date,
                'end_date': end_date,
                'order_count_today': order_count_today,
                'total_price_today': total_price_today,
                'categories': categories,
                'data': data,
                'recent_orders': recent_orders,
                'top_selling_products': top_selling_products,
            }

            return render(request, 'authentication/adminpaenl.html', context)

    return HttpResponseBadRequest("Invalid request method.")




def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category')
    else:
        form = CategoryForm()
    
    return render(request, 'authentication/add_category.html', {'form': form})


def category(request):
    categories = Category.objects.all()
    category_statuses = {
        category.id: 'active' if category.is_active else 'soft-deleted'
        for category in categories
    }
    category_statuses_json = json.dumps(category_statuses)

    context = {
        'categories': categories,
        'category_statuses': category_statuses_json,  # Pass the category_statuses variable to the template
    }

    return render(request, 'authentication/category_list.html', context)


def product(request):
    products = Product.objects.all()
    return render(request, 'products/product.html', {'products': products})


from django.contrib import messages

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)

            # Check if the image field is empty
            if not product.image:
                messages.error(request, "Please upload an image for the product.")
                return render(request, 'products/add_product.html', {'form': form})

            product.save()
            messages.success(request, "Product added successfully.")
            return redirect('product')
    else:
        form = ProductForm()
    
    return render(request, 'products/add_product.html', {'form': form})


def edit_category(request, category_id):
    if request.method=='POST':
        name=request.POST['category_name']
        image=request.FILES.get('category_images')
        cat=Category.objects.get(id=category_id)
        cat.name=name
        if image:
            cat.image.save(image.name,image)
        cat.save()
        return redirect('category')
    category=Category.objects.get(id=category_id)
    return render(request, 'authentication/editcategory.html', {'category': category})



def product_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = ProductVariant.objects.filter(product=product)
    images = ProductImage.objects.filter(variant__product=product)
    context = {
        'product': product,
        'variants': variants,
        'images': images,
        'product_id': product_id,
    }
    return render(request, 'variant/variants_view.html', context)


def add_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            new_variant = form.save(commit=False)
            new_variant.product = product
            new_variant.save()

            # Handle image upload
            image = request.FILES.get('image')
            if image:
                ProductImage.objects.create(variant=new_variant, image=image)

            return redirect('product_variant', product_id=product_id)
    else:
        form = ProductVariantForm()

    context = {
        'product': product,
        'form': form,
    }

    return render(request, 'variant/add_variant.html', context)



def add_image(request):
    if request.method == 'POST':
        form = ProductImageformsForm(request.POST, request.FILES)  # Pass request.FILES for image uploads
        if form.is_valid():
            form.save()
            # Redirect to the success page or another page after successful form submission
            return redirect('product')
    else:
        form = ProductImageformsForm()

    return render(request, 'variant/add_image.html', {'form': form})



def download_order_pdf_sales(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Today's totals
    today_orders = Order.objects.filter(order_date__date=today)
    order_count_today = today_orders.count()
    total_price_today = today_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Weekly totals
    week_orders = Order.objects.filter(order_date__range=[week_ago, today])
    order_count_week = week_orders.count()
    total_price_week = week_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Monthly totals
    month_orders = Order.objects.filter(order_date__range=[month_ago, today])
    order_count_month = month_orders.count()
    total_price_month = month_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Top selling products
    top_selling_products_today = CartItems.objects.values('product__model_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    top_selling_products_week = CartItems.objects.filter(cart__created_at__range=[week_ago, today]).values('product__model_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    top_selling_products_month = CartItems.objects.filter(cart__created_at__range=[month_ago, today]).values('product__model_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]

    context = {
        'order_count_today': order_count_today,
        'total_price_today': total_price_today,
        'order_count_week': order_count_week,
        'total_price_week': total_price_week,
        'order_count_month': order_count_month,
        'total_price_month': total_price_month,
        'top_selling_products_today': top_selling_products_today,
        'top_selling_products_week': top_selling_products_week,
        'top_selling_products_month': top_selling_products_month,
    }

    html_content = render_to_string('profile/pdf_download.html', context)

    # Set the response content type as 'application/pdf' to indicate that it's a PDF file
    response = HttpResponse(content_type='application/pdf')

    # Set the filename for the downloaded file
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Generate the PDF content from the HTML using xhtml2pdf
    pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), response)

    if pdf.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


def sales(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Today's totals
    today_orders = Order.objects.filter(order_date__date=today)
    order_count_today = today_orders.count()
    total_price_today = today_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Weekly totals
    week_orders = Order.objects.filter(order_date__range=[week_ago, today])
    order_count_week = week_orders.count()
    total_price_week = week_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Monthly totals
    month_orders = Order.objects.filter(order_date__range=[month_ago, today])
    order_count_month = month_orders.count()
    total_price_month = month_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Top selling products
    top_selling_products_today = CartItems.objects.values('product__model_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    top_selling_products_week = CartItems.objects.filter(cart__created_at__range=[week_ago, today]).values('product__model_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    top_selling_products_month = CartItems.objects.filter(cart__created_at__range=[month_ago, today]).values('product__model_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]

    context = {
        'order_count_today': order_count_today,
        'total_price_today': total_price_today,
        'order_count_week': order_count_week,
        'total_price_week': total_price_week,
        'order_count_month': order_count_month,
        'total_price_month': total_price_month,
        'top_selling_products_today': top_selling_products_today,
        'top_selling_products_week': top_selling_products_week,
        'top_selling_products_month': top_selling_products_month,
    }

    return render(request,'profile/pdf_download.html', context)
  



def allsales(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    all_orders = Order.objects.all()

    if start_date and end_date:
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        all_orders = all_orders.filter(order_date__date__range=[start_date, end_date])

    all_sales = all_orders.values('order_date__date').annotate(
        total_orders=Sum(1),
        total_price=Sum('total_price'),
        total_items_sold=Sum('orderitem__quantity')  # Corrected field name
    ).order_by('order_date__date')

    context = {
        'all_sales': all_sales,
    }

    return render(request, 'profile/allsales.html', context)




def generate_pdf_report(context):
    html_content = render_to_string('profile/report.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), response)

    if pdf.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


def download_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    all_orders = Order.objects.all()

    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        all_orders = all_orders.filter(order_date__date__range=[start_date, end_date])

    all_sales = all_orders.values('order_date__date').annotate(
        total_orders=Sum(1),
        total_price=Sum('total_price'),
        total_items_sold=Sum('orderitem__quantity')
    ).order_by('order_date__date')

    context = {
        'all_sales': all_sales,
        'start_date': start_date,  # Pass start_date to the context
        'end_date': end_date,      # Pass end_date to the context
    }

    return generate_pdf_report(context)
