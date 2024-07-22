import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, EmailValidator
from django.db import models
from django.utils import timezone

from .constants import ONE_TIME_CODE_EXPIRY_MINUTES


# Модель пользователя
class CustomUser(AbstractUser):
    uid = models.UUIDField(
        verbose_name='Уникальный идентификатор',
        default=uuid.uuid4,
        editable=False
    )
    username = models.CharField(
        max_length=20,
        verbose_name='Имя пользователя',
        unique=True,
        validators=[
            MinLengthValidator(2),
        ],
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='Email',
        unique=True,
        validators=[
            MinLengthValidator(6),
            EmailValidator,
        ],
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=20,
        validators=[
            MinLengthValidator(2),
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=20,
        validators=[
            MinLengthValidator(2),
        ]
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class OneTimeCode(models.Model):
    code = models.CharField(max_length=10)
    user = models.CharField(max_length=255)
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    def is_expired(self):
        expires_at = self.created_at + timezone.timedelta(
            minutes=ONE_TIME_CODE_EXPIRY_MINUTES
        )
        return timezone.now() > expires_at
