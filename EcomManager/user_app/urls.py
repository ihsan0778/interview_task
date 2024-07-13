# users/urls.py
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
    path('accounts/login/', views.CustomLoginView.as_view(template_name='user_app/login.html'), name='login'),
]