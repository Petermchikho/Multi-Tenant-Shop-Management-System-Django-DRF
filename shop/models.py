from django.db import models
from merchant.models import *
import uuid
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from datetime import datetime, timedelta
from decimal import Decimal

class Category(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4)
    name=models.CharField(max_length=100)
    image=models.ImageField(upload_to='category/',blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        self.image.delete(save=False)  # Delete the image file
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
    
# class Tag(models.Model):
#     id=models.UUIDField(primary_key=True,default=uuid.uuid4)
#     name=models.CharField(max_length=100)
#     slug = models.SlugField(unique=True, blank=True)

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             base_slug = slugify(self.name)
#             slug = base_slug
#             counter = 1
#             while Tag.objects.filter(slug=slug).exclude(pk=self.pk).exists():
#                 slug = f'{base_slug}-{counter}'
#                 counter += 1
#             self.slug = slug
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.name
    


STATUS=(
    ('new','new'),
    ('mid','mid'),
)
POPULARITY=(
    ('yes','yes'),
    ('no','no')
)

STOCK_REQUIRED = (('yes', 'yes'), ('no', 'no'))

class Product(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4)
    name=models.CharField(max_length=50)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='category')
    image=models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # final_price = models.DecimalField(max_digits=10, decimal_places=2)
    new=models.CharField(max_length=20,choices=STATUS,default='mid')
    popular=models.CharField(max_length=20,choices=POPULARITY,default='no')
    discount=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    requires_stock=models.CharField(max_length=20,choices=STOCK_REQUIRED,default='yes')
    quantity=models.IntegerField(default=1)
    description=RichTextUploadingField(verbose_name='The product description')
    sku=models.CharField(max_length=20,unique=True, blank=True)
    shop=models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            count = Product.objects.count() + 1
            sku = f"SKU-{count:03d}"  # Format: SKU-001, SKU-002...
            while Product.objects.filter(sku=sku).exclude(pk=self.pk).exists():
                count += 1
                sku = f"SKU-{count:03d}"
            self.sku = sku

        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        # if self.discount > 0:
        #     if self.discount >= self.price:
        #         raise ValueError("Discount cannot be equal to or greater than the price.")
        #     self.price = Decimal(self.price) - Decimal(self.discount)
        super().save(*args, **kwargs)
    
    @property
    def final_price(self):
        if self.discount > 0:
            if self.discount >= self.price:
                raise ValueError("Discount cannot be equal to or greater than the price.")
            return self.price - self.discount
        return self.price

    
    def decrease_stock(self, quantity=1):
        if self.requires_stock == "yes":
            if self.quantity >= quantity:
                self.quantity -= quantity
                self.save()
            else:
                raise ValueError(f"Not enough stock for {self.name}")

    class Meta:
        ordering=['-created_at']

    def __str__(self):
        return self.name
    def delete(self, *args, **kwargs):
        self.image.delete(save=False)  # Delete the image file
        super().delete(*args, **kwargs)

class ProductImages(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
    image=models.ImageField(upload_to='products/')

    def __str__(self):
        return f"{self.product.slug}-{self.id}"
    def delete(self, *args, **kwargs):
        self.image.delete(save=False)  # Delete the image file
        super().delete(*args, **kwargs)

AGREEMENT=(
    ('yes','yes'),
    ('no','no')
) 

class ProductAdditionalInfo(models.Model):
    
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="additional_info")

    # Universal fields (for all product types)
    brand = models.CharField(max_length=100, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    country_of_origin = models.CharField(max_length=100, blank=True, null=True)
    alcohol_percentage = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    size=models.CharField(max_length=100, blank=True, null=True)
    is_fragile = models.CharField(max_length=20, choices=AGREEMENT, default='no', blank=True, null=True)
   
    # --- Food / Chemical Specific Fields ---
    ingredients = models.TextField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    allergens = models.TextField(blank=True, null=True)

    # --- Electronics Specific Fields ---
    warranty_period = models.CharField(max_length=50, blank=True, null=True)
    power_rating = models.CharField(max_length=50, blank=True, null=True)
    technical_specs = models.TextField(blank=True, null=True)
    
def generate_order_id():
    return str(uuid.uuid4()).replace('-', '').upper()[:12]

BOOKED=(
    ('yes','yes'),
    ('no','no')
) 

class Table(models.Model):
    id= models.CharField(max_length=20,primary_key=True, unique=True, default=generate_order_id)
    shop=models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='table')
    number = models.IntegerField(unique=True)
    capacity = models.IntegerField()
    image=models.ImageField(upload_to='table/')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"Table {self.number}")
            slug = base_slug
            count = 1
            # Defensive loop to ensure slug uniqueness, in case of any rare conflicts
            while Table.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)


STATUS=(
    ('initiated','initiated'),
    ('pending','pending'),
    ('cancelled','cancelled'),
    ('failed','failed'),
    ('paid','paid'),
    ('delivered','delivered')
)
TAKEAWAY=(
    ('yes','yes'),
    ('no','no')
) 
BOOKING=(
    ('yes','yes'),
    ('no','no')
) 
DELIVERY=(
    ('yes','yes'),
    ('no','no')
) 
class Order(models.Model):
    order_id = models.CharField(max_length=20,primary_key=True, unique=True, default=generate_order_id)
    shop=models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='order')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    first_name=models.CharField(max_length=200, null=True, blank=True)
    last_name=models.CharField(max_length=200, null=True, blank=True)
    email=models.EmailField(max_length=200, null=True, blank=True)
    location=models.CharField(max_length=200, null=True, blank=True)
    phone=models.CharField(max_length=200,null=True, blank=True)
    status=models.CharField(max_length=100,choices=STATUS,default='initiated')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    transaction_id=models.CharField(max_length=200,blank=True, null=True)
    takeaway=models.CharField(max_length=20,choices=TAKEAWAY,default='no')
    booking_status=models.CharField(max_length=20,choices=BOOKING,default='no')
    delivery_status=models.CharField(max_length=20,choices=DELIVERY,default='no')
    date = models.DateField(blank=True,null=True)
    time = models.TimeField(blank=True,null=True) 
    custom_amount = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,help_text="Manual amount for non-product orders")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']

    def __str__(self):
        return f"{self.order_id}-{self.email}"
    @property
    def total_amount(self):
        if self.order_items.exists():
            return sum(item.quantity * item.product.final_price for item in self.order_items.all())
        return self.custom_amount or 0

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='order_items')
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()

    @property
    def item_subtotal(self):
        return self.product.final_price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order {self.order.order_id}"

CANCELLED=(
    ('yes','yes'),
    ('no','no')
)     

class Booking(models.Model):
    order=models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    shop=models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='booking')
    booking_cancelled=models.CharField(max_length=20,choices=CANCELLED,default='no')
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    phone=models.CharField(max_length=200)
    email=models.EmailField(max_length=200, null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField() 
    end_time = models.TimeField(blank=True, null=True)  # allow null so we can auto-set
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-created_at']

    def save(self, *args, **kwargs):
        if self.start_time and not self.end_time:
            start_dt = datetime.combine(self.date, self.start_time)
            end_dt = start_dt + timedelta(hours=1)
            self.end_time = end_dt.time()
        super().save(*args, **kwargs)

DELIVERY_STATUS=(
    ('initiated','initiated'),
    ('paid','paid'),
    ('delivered','delivered')
)

class Delivery(models.Model):
    order=models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    shop=models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='Delivery')
    delivery_cancelled=models.CharField(max_length=20,choices=CANCELLED,default='no')
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    phone=models.CharField(max_length=200)
    location=models.CharField(max_length=200)
    email=models.EmailField(max_length=200, null=True, blank=True)
    time = models.TimeField()
    status=models.CharField(max_length=20,choices=DELIVERY_STATUS,default='initiated')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-created_at']

    def __str__(self):
        return f"{self.first_name}-{self.email}"



