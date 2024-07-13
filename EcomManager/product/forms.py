from django import forms

class GenerateDummyProductsForm(forms.Form):
    count = forms.IntegerField(label='Number of dummy products to generate')
