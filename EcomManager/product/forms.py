from django import forms
from .models import Product, Category

class GenerateDummyProductsForm(forms.Form):
    count = forms.IntegerField(label='Number of dummy products to generate')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['id', 'category', 'title', 'description', 'price', 'video']

    price = forms.DecimalField(
        min_value=0.01,  # Minimum price value
        max_value=99999.99,  # Maximum price value
        max_digits=10,  # Maximum number of digits in total
        decimal_places=2,  # Maximum number of decimal places
        widget=forms.NumberInput(attrs={
            'step': '0.01'  # Step size for the input, useful for HTML5 input
        })
    )

class ProductupdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['id','category', 'title', 'description', 'price', 'video']        
     
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']        
        