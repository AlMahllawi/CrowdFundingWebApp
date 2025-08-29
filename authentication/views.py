import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import generate_activation_token
from .forms import RegistrationForm

logger = logging.getLogger("auth")
User = get_user_model()


def render_registration_form(request, form, error_message=None):
    if error_message:
        messages.error(request, error_message)
    return render(request, "auth/register.html", {"form": form})


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        if not form.is_valid():
            return render_registration_form(request, form, "Please correct the errors.")

        user = form.save(commit=False)
        user.is_active = False
        user.save()

        uid, token = generate_activation_token(user)
        content = render_to_string(
            "auth/activation-email.html",
            {
                "activation_link": f"{request.scheme}://{request.get_host()}"
                + f"/auth/activate/{uid}/{token}/",
                "user": user,
            },
        )
        email_message = EmailMultiAlternatives(
            subject="Account Activation",
            body=strip_tags(content),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email_message.attach_alternative(content, "text/html")

        
        email_message.send(fail_silently=True)
        messages.success(
            request, "Please check your email to activate your account."
        )
        return redirect("home:index")
    else:
        form = RegistrationForm()

    return render_registration_form(request, form)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, "Your account has been activated successfully! You can now log in."
        )
        return redirect("home:index")
    else:
        messages.error(request, "The activation link is invalid or has expired.")
        return redirect("register")
