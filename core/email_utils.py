"""
Утилиты для email-верификации и токенов
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Генератор токенов для верификации email
    """
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


email_verification_token = EmailVerificationTokenGenerator()


def send_verification_email(request, user):
    """
    Отправляет письмо с ссылкой для верификации email
    
    Args:
        request: HTTP request объект
        user: User модель
    """
    # Генерируем токен
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Формируем ссылку активации
    verification_url = request.build_absolute_uri(
        reverse('email_verify', kwargs={'uidb64': uid, 'token': token})
    )
    
    # Тема и текст письма
    subject = f'🦁 Подтвердите ваш email на ЗооБозор'
    message = f"""
Добро пожаловать на ЗооБозор, {user.username}!

Для завершения регистрации, пожалуйста, подтвердите ваш email адрес, перейдя по ссылке ниже:

{verification_url}

Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.

С уважением,
Команда ЗооБозор 🦁
    """
    
    # Отправляем письмо
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def verify_email_token(uidb64, token):
    """
    Проверяет токен верификации email
    
    Args:
        uidb64: Закодированный user ID
        token: Токен верификации
        
    Returns:
        User объект если токен валиден, иначе None
    """
    from django.contrib.auth.models import User
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if email_verification_token.check_token(user, token):
            return user
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass
    
    return None
