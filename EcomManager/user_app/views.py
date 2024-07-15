from django.shortcuts import render, redirect
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
from .forms import CustomUserCreationForm
from django.views.generic import FormView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class SignUpView(FormView):
    template_name = 'user_app/signup.html'
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Send email verification
        current_site = get_current_site(self.request)
        mail_subject = 'Activate your account'
        message = render_to_string('user_app/activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'token': default_token_generator.make_token(user),
            'uid': urlsafe_base64_encode(force_bytes(user.pk))
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()

        return redirect('account_activation_sent')

    def get_success_url(self):
        return redirect('account_activation_sent')

def account_activation_sent(request):
    return render(request, 'user_app/account_activation_sent.html')
def activate(request, uidb64, token):
    try:
        # Decode uidb64 to user id
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)

        # Check if token is valid for the user
        if default_token_generator.check_token(user, token):
            # Activate user account
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been activated. You can now log in.')
        else:
            messages.error(request, 'Activation link is invalid.')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        messages.error(request, 'Activation link is invalid.')
    
    return redirect('login')  # Redirect to login page after activation

@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginView(BaseLoginView):
    """
    Custom login view to return JWT token along with user info.
    """
    def form_valid(self, form):
        # Log the user in
        auth_login(self.request, form.get_user())

        # Generate JWT token
        user = self.request.user
        refresh = RefreshToken.for_user(user)

        # Customize data to return (add more as needed)
        data = {
            'token': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role,
                # Add more user data fields as needed
            }
        }
        
        return JsonResponse(data)

    def form_invalid(self, form):
        # Handle invalid login attempt
        return JsonResponse({'error': 'Invalid credentials'}, status=400)