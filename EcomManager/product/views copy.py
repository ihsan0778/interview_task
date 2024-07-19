# product/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Product, Category
from .permissions import IsAdminOrReadOnly, IsStaffOrReadOnly, IsAgentOrReadOnly
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from utils.utility import encrypt_data, decrypt_data
from django.shortcuts import render, redirect
from .forms import GenerateDummyProductsForm
from django.core.management import call_command
from django.http import HttpResponse
from .tasks import generate_dummy_data
import csv
from openpyxl import Workbook
from django.views.generic.base import View


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    permission_classes = [IsAdminOrReadOnly]
    
@method_decorator(csrf_exempt, name='dispatch')
class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'product/product_form.html'
    fields = ['category', 'title', 'description', 'price']
    success_url = reverse_lazy('product-list')
 #Added for data encripting but key error occurs
    # def form_valid(self, form):
    #     # Encrypt specific fields before saving
    #     encrypted_title = encrypt_data(form.cleaned_data['title'])
    #     encrypted_description = encrypt_data(form.cleaned_data['description'])

    #     # Replace form data with encrypted values
    #     form.instance.title = encrypted_title['ciphertext']
    #     form.instance.description = encrypted_description['ciphertext']

    #     # Set the uploaded_by field to the current user
    #     form.instance.uploaded_by = self.request.user

    #     return super().form_valid(form)
    def form_valid(self, form):
        form.instance.created_by = self.request.user 
        return super().form_valid(form)
class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    template_name = 'product/product_form.html'
    fields = ['category', 'title', 'description', 'price']
    permission_classes = [IsAdminOrReadOnly | IsStaffOrReadOnly]
    success_url = reverse_lazy('product-list')

    def test_func(self):
        return self.request.user.role in ['admin', 'staff']

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('product-list')
    template_name = 'product/product_confirm_delete.html'
    permission_classes = [IsAdminOrReadOnly]

    def test_func(self):
        return self.request.user.role == 'admin'

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    permission_classes = [IsAdminOrReadOnly]

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'product/category_form.html'
    fields = ['name']
    permission_classes = [IsAdminOrReadOnly]
    success_url = reverse_lazy('category_list')


class CategoryListView(ListView):
    model = Category
    template_name = 'product/category_list.html'
    
class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    template_name = 'product/category_form.html'
    fields = ['name']
    success_url = reverse_lazy('category-list')
    #permission_classes = [IsAdminOrReadOnly]

    def test_func(self):
        return self.request.user.role == 'admin'

class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('category-list')
    template_name = 'product/category_confirm_delete.html'
    permission_classes = [IsAdminOrReadOnly]

    def test_func(self):
        return self.request.user.role == 'admin'
    
    
def generate_dummy_products_view(request):
    if request.method == 'POST':
        form = GenerateDummyProductsForm(request.POST)
        if form.is_valid():
            count = form.cleaned_data['count']
            # Generate dummy products using management command
            call_command('generate_dummy_products',count=str(count))
            # Redirect to the product creation view after generating products
            return redirect('product-create')
    else:
        form = GenerateDummyProductsForm()

    return render(request, 'product/generate_dummy_products.html', {'form': form})

def trigger_dummy_data_generation(request):
    num_categories = 5
    num_products = 10
    generate_dummy_data.delay(num_categories, num_products)
    return HttpResponse("Dummy data generation triggered")

def export_products(request):
    return render(request, 'product/export_products.html')

class ProductExportView(View):
    def get(self, request, *args, **kwargs):
        format_type = request.GET.get('format', 'csv')  # Default to CSV if format not specified

        products = Product.objects.all()

        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="products.csv"'

            writer = csv.writer(response)
            writer.writerow(['Title', 'Description', 'Price', 'Status', 'Created At', 'Updated At', 'Uploaded By'])

            for product in products:
                writer.writerow([
                    product.title,
                    product.description,
                    product.price,
                    product.status,
                    product.created_at,
                    product.updated_at,
                    product.created_by.username  # Assuming uploaded_by is a User object
                ])

            return response

        elif format_type == 'excel':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="products.xlsx"'

            wb = Workbook()
            ws = wb.active
            ws.append(['Title', 'Description', 'Price', 'Status', 'Created At', 'Updated At', 'Uploaded By'])

            for product in products:
                ws.append([
                    product.title,
                    product.description,
                    product.price,
                    product.status,
                    product.created_at,
                    product.updated_at,
                    product.created_by.username  # Assuming uploaded_by is a User object
                ])

            wb.save(response)
            return response

        else:
            return HttpResponse("Invalid format requested", status=400)