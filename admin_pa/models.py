from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_image')
    # bannerimage = models.ImageField(upload_to='category_images')
    slug = models.SlugField(blank=True, max_length=250, unique=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('cat', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    short_description = models.TextField()
    image = models.ImageField(upload_to='product_image', default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(blank=True)
    is_active = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name


from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class size(models.Model):
    size = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)  # Define the slug field

    def __str__(self):
        return str(self.size)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.size)  # Populate the slug field
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


from django.db import models

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="productvariant")
    model_name = models.CharField(max_length=250)
    size = models.ForeignKey(size, on_delete=models.CASCADE)  # You mentioned size model
    store_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField(null=True, blank=True)
    color = models.ManyToManyField(Color, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    slug = models.SlugField(blank=True, unique=True)  # Removed sluggify
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Removed slug generation logic

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color} - {self.slug}"


class ProductImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')


class SalesReport(models.Model):
    date = models.DateField()
    total_sales = models.FloatField()
    total_orders = models.IntegerField()
    # Add more fields as needed, like top-selling products, average order value, etc.


class Offer(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.category} - {self.discount_percentage}% Off"
