from celery import shared_task
from django.core.mail import EmailMessage


@shared_task
def send_match_email(to_email, match_name):
    message = 'Вы понравились "{}"! Почта участника: {}'.format(match_name, to_email)
    email = EmailMessage(
        subject='У вас есть пара!',
        body=message,
        to=[to_email],
    )
    email.send()
