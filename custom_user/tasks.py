from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from datetime import datetime


@shared_task(name='newletter_to_users')
def send_newsletter():
    subject='Your confirmation'

    users=User.objects.all()

    for user in users:
        # body = render_to_string('a_messageboard/newsletter.html', {'name': user.first_name})
        # body='Just testing'
        # email = EmailMessage( subject, body, to=[user.email] )
        # # email.content_subtype = "html"
        # email.send()
        print(f"task initiated schedules {user.email}")
        send_mail('Your test', f'Your OTP is okay', 'info@mobipay.mw', [user.email])
    
    current_month = datetime.now().strftime('%B') 
    user_count = users.count()   
    return f'{current_month} Newsletter to {user_count} subs'