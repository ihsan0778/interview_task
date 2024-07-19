from django import forms
from .models import Product, Category

class GenerateDummyProductsForm(forms.Form):
    count = forms.IntegerField(label='Number of dummy products to generate')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['id','category', 'title', 'description', 'price', 'video']
     
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']        
        