"""Forms used by the auth pages."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class StyledFormMixin:
    """Add Bootstrap-friendly placeholders to every visible field."""

    placeholders = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.placeholders:
                field.widget.attrs.setdefault("placeholder", self.placeholders[name])


class RegistrationForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Used to identify your account. You can use a made-up address for this demo.",
    )
    placeholders = {
        "username": "Choose a username",
        "email": "you@example.com",
        "password1": "At least 8 characters",
        "password2": "Repeat your password",
    }

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(StyledFormMixin, AuthenticationForm):
    placeholders = {"username": "Username", "password": "Password"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Username"
        self.fields["password"].label = "Password"


class EmployeeUserCreationForm(StyledFormMixin, UserCreationForm):
    """Create a Django user for a staff member (used by the seed/demo and admin)."""

    class Meta:
        model = User
        fields = ("username", "password1", "password2")
