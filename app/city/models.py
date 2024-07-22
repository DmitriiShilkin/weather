from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone

from sign.models import CustomUser


# Модель городов для получения подсказок ввода и географических координат для API
class City(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=64,
        validators=[
            MinLengthValidator(4),
        ]
    )
    name_ascii = models.CharField(
        verbose_name='Название в кодировке ascii',
        max_length=64,
        validators=[
            MinLengthValidator(4),
        ]
    )
    latitude = models.FloatField(
        verbose_name='Широта',
        max_length=32
    )
    longitude = models.FloatField(
        verbose_name='Долгота',
        max_length=32
    )
    country = models.CharField(
        verbose_name='Страна',
        max_length=64,
        validators=[
            MinLengthValidator(4),
        ]
    )
    iso2 = models.CharField(
        verbose_name='Сокращенное название ISO-2',
        max_length=2,
        validators=[
            MinLengthValidator(2),
        ]
    )
    iso3 = models.CharField(
        verbose_name='Сокращенное название ISO-3',
        max_length=3,
        validators=[
            MinLengthValidator(3),
        ]
    )
    region = models.CharField(
        verbose_name='Регион/область',
        max_length=128,
        validators=[
            MinLengthValidator(4),
        ]
    )
    population = models.PositiveIntegerField(
        verbose_name='Население',
    )

    def __str__(self):
        return f'{self.name} ({self.country}, {self.region})'


# Модель для истории запросов погоды
class History(models.Model):
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False
    )
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.city.name} ({self.city.country}, {self.city.region})'
