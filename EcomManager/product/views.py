"""
Views for managing products and categories.
"""

from django.views.generic import ListView, CreateView, UpdateView,\
     DeleteView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Product, Category
from .permissions import IsAdminPermission, IsStaffPermission, IsAgentPermission
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from utils.utility import encrypt_data, decrypt_data
from django.shortcuts import render, redirect, get_object_or_404
from .forms import GenerateDummyProductsForm
from django.http import HttpResponse, HttpResponseForbidden
from .tasks import generate_dummy_data, process_video
import csv
from openpyxl import Workbook
from django.contrib.auth.decorators import user_passes_test
from .decorators import admin_required, staff_or_admin_required, \
     admin_or_agent_permissionrequired
from django.http import Http404     
from django.core.exceptions import ValidationError
from django.http import JsonResponse

class ProductListView(LoginRequiredMixin, ListView):
    """
    View for listing all products.
    """
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    permission_classes = [IsAdminPermission]

@method_decorator(admin_or_agent_permissionrequired, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ProductCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new product.
    """
    model = Product
    template_name = 'product/product_form.html'
    fields = ['category', 'title', 'description', 'price', 'video']
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        """
        Handles form submission for creating a new product.
        """
        form.instance.created_by = self.request.user 
        video_file = form.cleaned_data.get('video', None)
        if video_file:
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
            process_video.delay(instance.id, video_file.name, video_file.size)

            # Return JSON response for AJAX requests if needed
            return JsonResponse({'message': 'Video uploaded and processing started.'})

        return super().form_valid(form)

@method_decorator(admin_or_agent_permissionrequired, name='dispatch')
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing product.
    """
    model = Product
    template_name = 'product/product_form.html'
    fields = ['category', 'title', 'description', 'price']
    success_url = reverse_lazy('product-list')

    def get_object(self, queryset=None):
        """
        Returns the object to be deleted.
        Raises Http404 if no object is found matching the given query parameters.
        """
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs['pk'])
    
@method_decorator(admin_or_agent_permissionrequired, name='dispatch')
class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting an existing product.
    """
    model = Product
    success_url = reverse_lazy('product-list')
    template_name = 'product/product_confirm_delete.html'

    def get_object(self, queryset=None):
        """
        Returns the object to be deleted.
        Raises Http404 if no object is found matching the given query parameters.
        """
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs['pk'])
    
    
class CategoryListView(LoginRequiredMixin, ListView):
    """
    View for listing all categories.
    """
    model = Category
    template_name = 'product/category_list.html'
    context_object_name = 'categories'

@method_decorator(admin_required, name='dispatch')
class CategoryCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new category.
    """
    model = Category
    template_name = 'product/category_form.html'
    fields = ['name']
    permission_classes = [IsAdminPermission]
    success_url = reverse_lazy('category-list')

@method_decorator(admin_required, name='dispatch')
class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing category.
    """
    model = Category
    template_name = 'product/category_form.html'
    fields = ['name']
    success_url = reverse_lazy('category-list')

    def get_object(self, queryset=None):
        """
        Returns the object to be deleted.
        Raises Http404 if no object is found matching the given query parameters.
        """
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs['pk'])
    
@method_decorator(admin_required, name='dispatch')
class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View for deleting an existing category.
    """
    model = Category
    success_url = reverse_lazy('category-list')
    template_name = 'product/category_confirm_delete.html'
    permission_classes = [IsAdminPermission]

    def test_func(self):
        """
        Checks if the current user has permission to delete the category.
        """
        return self.request.user.role == 'admin'


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
