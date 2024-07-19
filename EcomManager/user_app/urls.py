# users/urls.py
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),
    path('activate/<str:uidb64>/<str:token>/', views.ActivateAccountView.as_view(), name='activate'),
    path('account_activation_sent/', views.AccountActivationSentView.as_view(), name='account_activation_sent'),
    path('accounts/login/', views.CustomLoginView.as_view(template_name='user_app/login.html'), name='login'),
]