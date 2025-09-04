import re
from datetime import date
from django import forms
from django.utils import timezone
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User

UserModel = get_user_model()


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "image"]

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"autofocus": True})
    )

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user_cache = authenticate(
                self.request, username=email, password=password
            )

            if self.user_cache is None:
                try:
                    user = User.objects.get(email=email)
                    if not user.is_active:
                        raise forms.ValidationError(
                            "Activate your account first (check your email) to be able to login.",
                            code="inactive",
                        )
                except UserModel.DoesNotExist:
                    pass  # User doesn't exist, proceed with generic error
                raise forms.ValidationError(
                    "Invalid email or password.", code="invalid_login"
                )

        return self.cleaned_data


class ProfileForm(UserChangeForm):
    birthdate = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Birth Date",
    )
    facebook_profile = forms.URLField(
        required=False,
        label="Facebook Profile",
        validators=[
            RegexValidator(
                regex=r"^https?://(www\.)?facebook\.com/[\w\.\-]+/?$",
                message="Please enter a valid Facebook profile URL.",
            )
        ],
    )
    country = forms.ChoiceField(
        choices=[("Egypt", "Egypt"), ("Others", "Others")],
        required=False,
        label="Country",
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "image",
            "birthdate",
            "facebook_profile",
            "country",
        ]
        widgets = {
            "email": forms.EmailInput(attrs={"disabled": "disabled"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("password", None)

    def clean_birthdate(self):
        birthdate = self.cleaned_data.get("birthdate")
        if birthdate:
            today = date.today()
            age = (
                today.year
                - birthdate.year
                - ((today.month, today.day) < (birthdate.month, birthdate.day))
            )
            if age < 18:
                raise ValidationError("You must be at least 18 years old.")
        return birthdate


class DeleteAccountForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not authenticate(email=self.user.email, password=password):
            raise ValidationError("Incorrect password")
        return password
