from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_match_email(to_email, match_email):
    send_mail(
        'You have a match!',
        f'You matched with {match_email}!',
        'from@example.com',
        [to_email],
        fail_silently=False,
    )
