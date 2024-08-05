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
from utils.utility import encrypt_data, decrypt_data,encrypt_object_fields,decrypt_object_fields
from django.shortcuts import render, redirect, get_object_or_404
from .forms import GenerateDummyProductsForm, ProductForm, CategoryForm,ProductupdateForm
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest,\
    Http404
from .tasks import generate_dummy_data, process_video
from openpyxl import Workbook
from .decorators import admin_required, staff_or_admin_required, \
     admin_or_agent_permissionrequired   
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
import json
from urllib.parse import unquote, parse_qs

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(admin_or_agent_permissionrequired, name='dispatch')
class ProductListView(View):
    def get(self, request):
        is_admin_or_staff = request.user.is_superuser or hasattr(request.user, 'profile') and \
                            request.user.profile.role in ['admin', 'staff']
        
        if request.user.is_superuser:
            products = Product.objects.all()
        else:
            products = Product.objects.filter(created_by=request.user)
        
        form = ProductForm()
        
        context = {
            'products': products,
            'form': form,
            'is_admin_or_staff': is_admin_or_staff,
        }
        
        return render(request, 'product/product_list.html', context)

    def post(self, request):
        action = request.POST.get('action')
        if action == 'add':
            form = ProductForm(request.POST or None)
            video_file = None 
            form.instance.created_by = self.request.user
            if 'video' in request.FILES:
                video_file = request.FILES['video']
                total_size = video_file.size
                # Validate total size for multiple video uploads
                for product in Product.objects.all():
                    total_size += product.video.size if product.video else 0
                if total_size > 20 * 1024 * 1024:  # 20 MB
                     return HttpResponseBadRequest("Total video size cannot exceed 20 MB")
            
            if form.is_valid():
                instance = form.save(commit=False)
                if request.user.role == "admin":
                    instance.status = "approved"
                instance.save()
            # Call Celery task for video processin
                if video_file:
                    products = Product.objects.all()
                    video_content = video_file.read()
                    video_base64 = base64.b64encode(video_content).decode('utf-8')
                    process_video.delay(instance.id, video_file.name, video_file.size, video_base64)
                    return render(request, 'product/product_list.html', {'products': products, 'form': form})
                else:
                    products = Product.objects.all()
                    return render(request, 'product/product_list.html', {'products': products, 'form': form})
        elif action == 'update':
            product = get_object_or_404(Product, pk=request.POST['product_id'])
            form = ProductForm(request.POST,instance=product)
            video_file = None 
            if form.is_valid():
                if 'video' in request.FILES:
                    video_file = request.FILES['video']
                    total_size = video_file.size
                    # Validate total size for multiple video uploads
                    for product in Product.objects.all():
                        total_size += product.video.size if product.video else 0
                    if total_size > 20 * 1024 * 1024:  # 20 MB
                        return HttpResponseBadRequest("Total video size cannot exceed 20 MB")
                instance = form.save(commit=False)
                instance.save()
                if video_file:
                    products = Product.objects.all()
                    video_content = video_file.read()
                    video_base64 = base64.b64encode(video_content).decode('utf-8')
                    process_video.delay(instance.id, video_file.name, video_file.size, video_base64)
                    return render(request, 'product/product_list.html', {'products': products, 'form': form})
                products = Product.objects.all()
                form = ProductForm()
                return redirect('product_list')
            else:
                form=ProductForm(instance=product)
                return render(request, 'product/product_update.html', {'form': form, 'product': product})
   
       
    def delete(self, request, *args, **kwargs):
        import json
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        product.delete()
        return JsonResponse({'message': 'Product deleted successfully'})


       
    
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

        export_function = {
            'csv': self.export_to_csv,
            'excel': self.export_to_excel
        }.get(format_type, self.invalid_format)

        return export_function()

    def export_to_csv(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        self._write_csv_header(writer)
        self._write_product_data(writer)

        return response

    def export_to_excel(self):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="products.xlsx"'

        wb = Workbook()
        ws = wb.active
        self._write_excel_header(ws)
        self._write_product_data(ws, is_excel=True)

        wb.save(response)
        return response

    def _write_csv_header(self, writer):
        writer.writerow(['Title', 'Description', 'Price', 'Status', 'Created At', 'Updated At', 'Uploaded By'])

    def _write_excel_header(self, ws):
        ws.append(['Title', 'Description', 'Price', 'Status', 'Uploaded By'])

    def _get_product_data(self, product, is_excel=False):
        data = [
            product.title,
            product.description,
            product.price,
            product.status,
            product.created_by.email
        ]
        if not is_excel:
            data.extend([product.created_at, product.updated_at])
        return data

    def _write_product_data(self, writer_or_ws, is_excel=False):
        products = Product.objects.all()
        for product in products:
            data = self._get_product_data(product, is_excel)
            if is_excel:
                writer_or_ws.append(data)
            else:
                writer_or_ws.writerow(data)

    def invalid_format(self):
        return HttpResponse("Invalid format requested", status=400)


@method_decorator(staff_or_admin_required, name='dispatch')     
class ProductApproveView(UpdateView):
    """
    View for approving or rejecting a product.
    """
    model = Product
    template_name = 'product/product_approve_reject_form.html'
    fields = ['status']
    success_url = reverse_lazy('product_list')
    
    def form_valid(self, form):
        """
        Handles form submission for approving or rejecting a product.
        """
        instance = get_object_or_404(Product, pk=self.object.pk)
        if instance.status != 'draft':
            return HttpResponseForbidden("You can only approve or reject products with status 'draft'.")
        if form.cleaned_data['status'] not in ['approved', 'rejected']:
            form.add_error('status', "Invalid status value. It must be either 'approved' or 'rejected'.")
            return self.form_invalid(form)
        # Update the instance fields
        instance.status = form.cleaned_data['status']
        instance.approved_by = self.request.user

        # Save the updated instance
        instance.save()
        return super().form_valid(form)
    def form_invalid(self, form):
        """
        Handle the invalid form case.
        """
        return self.render_to_response(self.get_context_data(form=form))
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

        return queryset


class EncryptView(View):
    def post(self, request):
        try:
            data = request.POST.get('data')
            if not data:
                return JsonResponse({'error': 'No data provided'}, status=400)
            
            encrypted_data = encrypt_data(data)
            return JsonResponse({'encrypted_data': encrypted_data}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class DecryptView(View):
    def post(self, request):
        try:
            encrypted_data = request.POST.get('data')
            if not encrypted_data:
                return JsonResponse({'error': 'No data provided'}, status=400)
            
            decrypted_data = decrypt_data(encrypted_data)
            return JsonResponse({'decrypted_data': decrypted_data}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
def test_encryption_view(request):
    return render(request, 'product/test_encryption.html')        