from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class BaseRegisterForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "last_name",
            "first_name",
            "password1",
            "password2",
        )


class CustomUserUpdateForm(UserChangeForm):
    email = forms.EmailField(
        disabled=True
    )
    username = forms.CharField(
        label="Имя пользователя",
        disabled=True
    )

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "last_name",
            "first_name",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields["password"]
