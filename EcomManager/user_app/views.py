from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.encoding import force_bytes
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView as BaseLoginView
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from django.views.generic import  TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.views import View
from django.http import HttpResponseBadRequest
from django.contrib.auth import logout
from django.urls import reverse

User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class UserListView(View):
    form_class = CustomUserCreationForm
    template_name = 'user_app/user_list.html'
    update_template_name = 'user_app/user_update.html'

    def post(self, request):
        action = request.POST.get('action')
        if action == 'add':
            if request.user.role == "admin":
                return self.handle_add(request)
            else:
                return JsonResponse({'error': 'Only admin have the permission to create user'}, status=400)
        elif action == 'update':
            return self.handle_update(request)
        elif action == 'delete':
            return self.handle_delete(request)
        return HttpResponseBadRequest("Invalid action")

    def handle_add(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Send email verification
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            message = render_to_string('user_app/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'token': token,
                'uid': uid
            })
            activation_link = f"http://{current_site.domain}{reverse('activate', kwargs={'uidb64':uid, 'token': token})}"
    
            print(f"Activation link: {activation_link}")
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()

            return redirect('account_activation_sent')
        else:
            users = User.objects.all()
            return render(request, self.template_name, {'users': users, 'form': form})

    def handle_update(self, request):
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        form = CustomUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
        else:
            return render(request, self.update_template_name, {'user': user,
                                                               'form': form})

    def handle_delete(self, request):
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        if user.is_superuser:
            return HttpResponseBadRequest("Invalid action")
        user.delete()
        return redirect('user_list')

    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.is_staff:
                users = User.objects.all()
            else:
                users = User.objects.filter(pk=request.user.pk)
            form = self.form_class()
            return render(request, self.template_name, {'users': users, 'form': form})
        else:
            return HttpResponseBadRequest("You are- not authorized view this page")

    def get_success_url(self):
        return reverse_lazy('account_activation_sent')

class AccountActivationSentView(TemplateView):
    """
    AccountActivationSentView:
    Renders a confirmation message after activation email is sent.
    """
    template_name = 'user_app/account_activation_sent.html'

    
class ActivateAccountView(View):
    """
    View for activating user account via email verification link.
    """

    def get(self, request, uidb64, token):
        """
        Handles GET request to activate user account.
        """
        try:
            # Decode uidb64 to user id
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)

            # Check if token is valid for the user
            if default_token_generator.check_token(user, token):
                # Activate user account
                user.is_active = True
                user.save()
                messages.success(request, 'Your account has been activated. You can now log in.')
            else:
                messages.error(request, 'Activation link is invalid.')
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'Activation link is invalid.')

        return redirect(reverse_lazy('login'))  # Redirect to login page after activation


@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginView(BaseLoginView):
   def form_valid(self, form):
        try:
            # Log the user in
            user = form.get_user()
            auth_login(self.request, user)

            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            data = {
                'token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': getattr(user, 'role', None), 
                }
            }

            return redirect('product_list')  

        except Exception as e:
            # Handle unexpected errors
            return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

def form_invalid(self, form):
        try:
            # Handle invalid login attempt
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
        except Exception as e:
            # Handle unexpected errors in invalid form case
            return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({'message': 'Successfully logged out'}, status=200)

    def get(self, request):
        return JsonResponse({'error': 'Invalid request method'}, status=400)

