from django.conf import settings
from django.core.mail import send_mail


# отправка одноразового кода при регистрации:
def send_one_time_code(code, user):
    send_mail(
        subject='Код активации',
        message=f'Код активации аккаунта: {code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
