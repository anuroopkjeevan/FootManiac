
from django import forms
from .models import Product, ProductImage
from .models import Category
from .models import ProductVariant
from django import forms
from .models import size

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'image', 'short_description']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image']
        




class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['model_name', 'size', 'store_price', 'sale_price', 'stock', 'discount_percentage',  'slug']

    # Add this method to enforce the required attribute for the slug field
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = True


class ProductImageformsForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['variant', 'image' ]
