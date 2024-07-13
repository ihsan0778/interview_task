# product/urls.py
from django.urls import path
from .views import (
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView
)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
    path('', CategoryListView.as_view(), name='category_list'), 
]
