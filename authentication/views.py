import logging
from smtplib import SMTPException
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
    get_user_model,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import IntegrityError
from .utils import generate_activation_token
from .forms import RegistrationForm, LoginForm


logger = logging.getLogger("auth")
User = get_user_model()


def register(request):
    if request.user.is_authenticated:
        return redirect("home:index")

    template = "auth/register.html"

    if request.method != "POST":
        return render(request, template, {"form": RegistrationForm()})

    form = RegistrationForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Please correct the errors.")
        return render(request, template, {"form": form})

    try:
        if User.objects.filter(email=form.cleaned_data.get("email")).exists():
            messages.error(
                request,
                "This email is already registered. Please use a different email or log in.",
            )
            return render(request, template, {"form": form})

        user = form.save(commit=False)
        user.is_active = False
        user.save()

        uid, token = generate_activation_token(user)
        content = render_to_string(
            "auth/activation-email.html",
            {
                "activation_link": f"{request.scheme}://{request.get_host()}"
                + reverse(
                    "authentication:activate", kwargs={"uidb64": uid, "token": token}
                ),
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

        try:
            email_message.send(fail_silently=False)
            messages.success(
                request, "Please check your email to activate your account."
            )
            return redirect("authentication:login")
        except SMTPException as e:
            logger.error("Failed to send activation email to %s: %s", user.email, e)
            user.delete()
            messages.error(
                request,
                "Failed to send activation email. Please try again later or contact support.",
            )
            return render(request, template, {"form": form})
    except IntegrityError as e:
        logger.error("Database error during registration for %s: %s", user.email, e)
        messages.error(
            request, "An error occurred during registration. Please try again."
        )
        return render(request, template, {"form": form})
    except Exception as e:  # pylint: disable=W0718
        logger.error("Unexpected error registering %s: %s", user.email, e)
        user.delete()
        messages.error(
            request,
            "An unexpected error occurred. Please try again or contact support.",
        )
        return render(request, template, {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if (
        user is None
        or user.is_active
        or not default_token_generator.check_token(user, token)
    ):
        messages.error(request, "The activation link is invalid or has expired.")
        return redirect("authentication:register")

    user.is_active = True
    user.save()
    messages.success(
        request, "Your account has been activated successfully! You can now log in."
    )

    return redirect("authentication:login")


def login(request):
    if request.user.is_authenticated:
        return redirect("home:index")

    template = "auth/login.html"

    if request.method != "POST":
        return render(request, template, {"form": LoginForm()})

    form = LoginForm(data=request.POST, request=request)
    if not form.is_valid():
        messages.error(request, "Please correct the errors.")
        return render(request, template, {"form": form})

    user = form.get_user()
    auth_login(request, user)
    messages.success(request, f"Welcome back, {user.first_name} {user.last_name}!")
    return redirect("home:index")


@login_required
def profile(request):
    return render(request, "auth/profile.html")


@login_required
def logout(request):
    auth_logout(request)
    return redirect("home:index")
