"""
Views for managing products and categories.
"""
import csv
import base64
from django.views.generic import ListView, CreateView, UpdateView,\
      FormView, View
from django.urls import reverse_lazy
from .models import Product, Category
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from utils.utility import encrypt_data, decrypt_data
from django.shortcuts import render, redirect, get_object_or_404
from .forms import GenerateDummyProductsForm, ProductForm, CategoryForm
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest,\
    Http404
from .tasks import generate_dummy_data, process_video
from openpyxl import Workbook
from .decorators import admin_required, staff_or_admin_required, \
     admin_or_agent_permissionrequired   
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render, redirect, get_object_or_404
from django.views import View

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(admin_or_agent_permissionrequired, name='dispatch')
class ProductListView(View):
    def get(self, request):
        products = Product.objects.all()
        form = ProductForm()
        return render(request, 'product/product_list.html', {'products': products, 'form': form})

    def post(self, request):
        action = request.POST.get('action')

        if action == 'add':
            form = ProductForm(request.POST)
            video_file = None 
            form.instance.created_by = self.request.user
            if 'video' in request.FILES:
                video_file = request.FILES['video']
                total_size = video_file.size
                # Validate total size for multiple video uploads
                for product in Product.objects.all():
                    total_size += product.video.size if product.video else 0
                if total_size > 20 * 1024 * 1024:  # 20 MB
                    form.add_error('video', ValidationError('Total video size cannot exceed 20 MB.'))
                    return self.form_invalid(form)
            
            # Save the product instance without committing to the database
            instance = form.save(commit=False)
            instance.save()
            # Call Celery task for video processing

            if form.is_valid():
                form.save()
                if video_file:
                    video_content = video_file.read()
                    video_base64 = base64.b64encode(video_content).decode('utf-8')
                    process_video.delay(instance.id, video_file.name, video_file.size, video_base64)
                return redirect('product_list')
            else:
                products = Product.objects.all()
                return render(request, 'product/product_list.html', {'products': products, 'form': form})

        elif action == 'update':
            product = get_object_or_404(Product, pk=request.POST['product_id'])
            form = ProductForm(request.POST,instance=product)
            if form.is_valid():
                form.save()
                products = Product.objects.all()
                return render(request, 'product/product_list.html', {'products': products, 'form': form})
            else:
                form=ProductForm(instance=product)
                return render(request, 'product/product_update.html', {'form': form, 'product': product})

        elif action == 'delete':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, pk=product_id)
            product.delete()
            return redirect('product_list')  # Replace with your URL name for product list

        return HttpResponseBadRequest("Invalid action")
    
class ProductDetailView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return render(request, 'product/product_detail.html', {'product': product})

@method_decorator(admin_required, name='dispatch')    
class CategoryListView(View):
    def get(self, request):
        categories = Category.objects.all()
        form = CategoryForm()
        return render(request, 'product/category_list.html', {'categories': categories, 'form': form})

    def post(self, request):
        action = request.POST.get('action')

        if action == 'add':
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('category_list')  # Replace with your URL name for category list
            else:
                categories = Category.objects.all()
                return render(request, 'product/category_list.html', {'categories': categories, 'form': form})

        elif action == 'update':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, pk=category_id)
            form = CategoryForm(request.POST,instance=category)
            if form.is_valid():
                form.save()
                return redirect('category_list')  # Replace with your URL name for category list
            else:
                form=CategoryForm(instance=category)
                return render(request, 'product/category_update.html', {'form': form, 'category': category})

        elif action == 'delete':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, pk=category_id)
            category.delete()
            return redirect('category_list')  # Replace with your URL name for category list

        return HttpResponseBadRequest("Invalid action")


@method_decorator(admin_required, name='dispatch')
class GenerateDummyProductsView(FormView):
    """
    View for generating dummy products based on user input.
    """
    template_name = 'product/generate_dummy_products.html'
    form_class = GenerateDummyProductsForm

    def form_valid(self, form):
        """
        Handles form submission for generating dummy products.
        """
        count = form.cleaned_data['count']
        
        # Creating 5 categories
        num_categories = 5
        num_products = int(count)  # Convert count to integer
        
        # Trigger dummy data generation
        generate_dummy_data(num_categories, num_products)
        
        return HttpResponse("Dummy data generation triggered")

def trigger_dummy_data_generation(request):
    """
    View for triggering dummy data generation asynchronously.
    """
    num_categories = 5
    num_products = 10
    generate_dummy_data.delay(num_categories, num_products)
    return HttpResponse("Dummy data generation triggered")

def export_products(request):
    """
    View for exporting products to CSV or Excel format.
    """
    return render(request, 'product/export_products.html')

class ProductExportView(View):
    """
    View for exporting products to CSV or Excel format.
    """
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
                    product.created_by.email
                ])

            return response

        elif format_type == 'excel':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="products.xlsx"'

            wb = Workbook()
            ws = wb.active
            ws.append(['Title', 'Description', 'Price', 'Status', 'Uploaded By'])
            for product in products:
                ws.append([
                    product.title,
                    product.description,
                    product.price,
                    product.status,
                    product.created_by.email
                ])

            wb.save(response)
            return response

        else:
            return HttpResponse("Invalid format requested", status=400)

@method_decorator(staff_or_admin_required, name='dispatch')     
class ProductApproveView(UpdateView):
    """
    View for approving or rejecting a product.
    """
    model = Product
    template_name = 'product/product_approve_reject_form.html'
    fields = ['status']
    success_url = reverse_lazy('product-list')
    
    def form_valid(self, form):
        """
        Handles form submission for approving or rejecting a product.
        """
        instance = get_object_or_404(Product, pk=self.object.pk)

        if instance.status != 'draft':
            return HttpResponseForbidden("You can only approve or reject products with status 'draft'.")

        # Update the instance fields
        instance.status = form.cleaned_data['status']
        instance.approved_by = self.request.user

        # Save the updated instance
        instance.save()
        return super().form_valid(form)

@method_decorator(admin_or_agent_permissionrequired, name='dispatch')
class ProductHistoryView(ListView):
    """
    View for displaying product history based on user role.
    """
    model = Product
    template_name = 'product/product_history.html'
    context_object_name = 'products'

    def get_queryset(self):
        """
        Retrieves queryset based on user role and optional filters.
        """
        queryset = Product.objects.none() 

        if self.request.user.role == 'admin':
            queryset = Product.objects.all()

        elif self.request.user.role == 'end_user':
            queryset = Product.objects.all().filter(created_by=self.request.user)

        # Filter by status if query parameter is provided
        show_rejected = self.request.GET.get('show_rejected')
        show_approved = self.request.GET.get('show_approved')

        if show_rejected:
            queryset = queryset.filter(status='rejected')
        elif show_approved:
            queryset = queryset.filter(status='approved')

        return queryset
