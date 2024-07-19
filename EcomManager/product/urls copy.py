# product/urls.py
from django.urls import path
from .views import (
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    generate_dummy_products_view, trigger_dummy_data_generation, ProductExportView,
    export_products
)

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('update/<int:pk>/', ProductUpdateView.as_view(), name='product-update'),
    path('delete/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),
    path('generate/', generate_dummy_products_view, name='generate-dummy-products'),
    
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/update/<int:pk>/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/delete/<int:pk>/', CategoryDeleteView.as_view(), name='category-delete'),
    path('', CategoryListView.as_view(), name='category_list'), 
    path('generate-dummy-data/', trigger_dummy_data_generation, name='generate-dummy-data'),
    path('start_export-products/', export_products, name='export-products'),
    path('export-products/', ProductExportView.as_view(), name='export-products'),
]
