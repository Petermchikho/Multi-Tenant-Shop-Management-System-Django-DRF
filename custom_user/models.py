from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models
from shop.models import Shop
from merchant.models import Merchant

class User(BaseUser):
    
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('merchant', 'Merchant'),
        ('seller', 'Seller'),
        ('buyer', 'Buyer'),
    )
    
    username=models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="buyer")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    merchant=models.ForeignKey(Merchant, null=True, blank=True, on_delete=models.SET_NULL)
    shop = models.ForeignKey(Shop, null=True, blank=True, on_delete=models.SET_NULL)
    

    objects = BaseUserManager()

    class Meta:
        ordering=['-id']

    def __str__(self):
        return f'{self.username} for {self.email}'
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')

        return self.create_user(username, email, password, **extra_fields)
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"