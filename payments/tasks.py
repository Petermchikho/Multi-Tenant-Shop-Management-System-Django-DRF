from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import requests


url = 'https://messaging.mobipay.mw/api/v1/sendsms'
apiKey = settings.VAS_API_KEY

@shared_task(name='sms_send')
def send_verification_sms_to_shop(sender, recipients, message):
    headers={
                'x-api-key': apiKey,
                'Content-Type': 'application/json',
            }
    if isinstance(recipients, str):
        recipients = [recipients]
    elif isinstance(recipients, list):
        recipients = [str(r).strip() for r in recipients]
    else:
        raise ValueError("Recipients must be a string or a list of strings")

    payload = {
                "from": f"{sender}",
                "recepients": recipients if isinstance(recipients, list) else [recipients],
                "message": f"{message}",
            }
 
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
                data = response.json()
                
    else:
        print(f"Failed to send SMS: {response.status_code} - {response.text}")
    return response.status_code

@shared_task(name='email_shop')
def send_verification_email(email,message):
    print("task initiated")
    send_mail(
        subject="Account Credited",
        message=message,
        from_email='info@mobipay.mw',
        recipient_list=[email],
        fail_silently=False
    )

    return email