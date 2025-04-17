from django.core.mail import send_mail
from django.conf import settings

def send_user_notification(subject, message, recipient_email):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
        [recipient_email],
        fail_silently=False,
    )
