from django.db import models
import uuid
from django.utils.text import slugify
import random

from django.utils import timezone

def generate_id():
    return str(uuid.uuid4()).replace('-', '').upper()[:12]
class Merchant(models.Model):
    id =  models.CharField(max_length=20,primary_key=True, unique=True, default=generate_id,editable=False)
    name = models.CharField(max_length=255)
    app_id = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Merchant"
        verbose_name_plural = "Merchants"
        ordering=['-created_at']

class ShopType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image=models.ImageField(upload_to='shop-type/',blank=True,null=True)
    shop_domain=models.URLField()
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while ShopType.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Shop Type"
        verbose_name_plural = "Shop Types"

class ActiveShopManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='active')

def generate_shop_id():
    while True:
        new_id = str(random.randint(1000000, 9999999))  # 7-digit random ID
        if not Shop.objects.filter(id=new_id).exists():
            return new_id

class Shop(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    id=models.CharField(max_length=20,primary_key=True, unique=True, default=generate_shop_id)
    name=models.CharField(max_length=100)
    address=models.CharField(max_length=255)
    location=models.CharField(max_length=255)
    phone=models.CharField(max_length=15)
    email=models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    tenant=models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='shops',)
    image=models.ImageField(upload_to='shop/',blank=True,null=True)
    logo=models.ImageField(upload_to='shop-logos/',blank=True,null=True)
    color_theme = models.CharField(max_length=20, blank=True,null=True)
    shop_type = models.ForeignKey(ShopType, on_delete=models.CASCADE, related_name='shops')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveShopManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        if self.status != 'inactive':
            self.status = 'inactive'
            self.deleted_at = timezone.now()
            self.save()

    def restore(self):
        if self.status == 'inactive':
            self.status = 'active'
            self.deleted_at = None
            self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Shop.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
