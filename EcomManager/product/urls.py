# # product/urls.py
# from django.urls import path, include
# from .views import ProductViewSet
# # (
# #     ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView,
# #     CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
# #     GenerateDummyProductsView, trigger_dummy_data_generation, ProductExportView,
# #     export_products, ProductApproveView, ProductHistoryView
# # )

# # urlpatterns = [
# #     path('', ProductListView.as_view(), name='product-list'),
# #     path('create/', ProductCreateView.as_view(), name='product-create'),
# #     path('update/<int:pk>/', ProductUpdateView.as_view(), name='product-update'),
# #     path('delete/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),
# #     path('generate-dummy-products/', GenerateDummyProductsView.as_view(), 
# #          name='generate-dummy-products'),
    
# #     path('categories/', CategoryListView.as_view(), name='category-list'),
# #     path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
# #     path('categories/update/<int:pk>/', CategoryUpdateView.as_view(), name='category-update'),
# #     path('categories/delete/<int:pk>/', CategoryDeleteView.as_view(), name='category-delete'),
# #     path('', CategoryListView.as_view(), name='category_list'), 
# #     path('generate-dummy-data/', trigger_dummy_data_generation, name='generate-dummy-data'),
# #     path('start_export-products/', export_products, name='export-products'),
# #     path('export-products/', ProductExportView.as_view(), name='export-products'),
# #     path('approve/<int:pk>/', ProductApproveView.as_view(), name='product-approve'),
# #     path('history/', ProductHistoryView.as_view(), name='product-history'),
# # ]
# # from rest_framework.routers import DefaultRouter
# # router = DefaultRouter()

# urlpatterns = [
#     path('product/', ProductViewSet.as_view(), name='product-crud'),
# ]


from django.urls import path

from .views import ProductListView, ProductDetailView, CategoryListView,EncryptView,DecryptView,\
test_encryption_view, GenerateDummyProductsView, ProductHistoryView, ProductApproveView, \
trigger_dummy_data_generation, export_products, ProductExportView


urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('encrypt/', EncryptView.as_view(), name='encrypt'),
    path('decrypt/', DecryptView.as_view(), name='decrypt'),
    path('test-encryption/', test_encryption_view, name='test_encryption'),
    path('generate-dummy-products/', GenerateDummyProductsView.as_view(), 
         name='generate-dummy-products'),
    path('generate-dummy-data/', trigger_dummy_data_generation, name='generate-dummy-data'),
     path('start_export-products/', export_products, name='export-products'),
    path('export-products/', ProductExportView.as_view(), name='export-products'),
     path('approve/<int:pk>/', ProductApproveView.as_view(), name='product-approve'),
    path('history/', ProductHistoryView.as_view(), name='product-history'),
]