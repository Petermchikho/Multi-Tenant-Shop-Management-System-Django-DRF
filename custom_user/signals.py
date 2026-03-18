from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from .models import Profile
from django.core.mail import send_mail,send_mass_mail
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save,sender=User,dispatch_uid="send_welcome_email")
def send_welcome_email(sender, instance, created, **kwargs):
    """ Send email """
    print("Signal Fired...")
    if created:
        send_mail(
            'Welcome!',
            'Thanks for signing up!',
            'info@mobipay.mw',
            [instance.email],
            fail_silently=False
        )
