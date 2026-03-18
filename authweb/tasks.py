from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import requests


url = 'https://messaging.mobipay.mw/api/v1/sendsms'
apiKey = settings.VAS_API_KEY

@shared_task(name='email_otp')
def send_otp_email(otp,email):
    print("task initiated")
    send_mail('Your OTP', f'Your OTP is {otp}', 'info@mobipay.mw', [email])

    return email

@shared_task(name='sms_send')
def send_sms(sender, recipients, message):
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


@shared_task(name='sms_send')
def send_invite_sms(sender, recipients, message):
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