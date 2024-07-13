# product/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Product, Category
from .permissions import IsAdminOrReadOnly, IsStaffOrReadOnly, IsAgentOrReadOnly
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

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

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user 
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    template_name = 'product_form.html'
    fields = ['category', 'title', 'description', 'price']
    permission_classes = [IsAdminOrReadOnly | IsStaffOrReadOnly]

    def test_func(self):
        return self.request.user.role in ['admin', 'staff']

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('product-list')
    template_name = 'product_confirm_delete.html'
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
    template_name = 'category/category_list.html'
    
class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    template_name = 'category_form.html'
    fields = ['name']
    #permission_classes = [IsAdminOrReadOnly]

    def test_func(self):
        return self.request.user.role == 'admin'

class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('category-list')
    template_name = 'category_confirm_delete.html'
    permission_classes = [IsAdminOrReadOnly]

    def test_func(self):
        return self.request.user.role == 'admin'
