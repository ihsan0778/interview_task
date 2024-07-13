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

User = get_user_model()


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
           
            # Send email verification
            current_site = get_current_site(request)
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
    else:
        form = CustomUserCreationForm()
    return render(request, 'user_app/signup.html', {'form': form})

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
            import pdb
            pdb.set_trace()
            messages.success(request, 'Your account has been activated. You can now log in.')
        else:
            messages.error(request, 'Activation link is invalid.')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        messages.error(request, 'Activation link is invalid.')
    
    return redirect('login')  # Redirect to login page after activation