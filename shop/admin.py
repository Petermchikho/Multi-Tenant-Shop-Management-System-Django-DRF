from django.contrib import admin
from .models import *
# Register your models here.
class ProductImagesInline(admin.TabularInline):
    model = ProductImages
class ProductAdmin(admin.ModelAdmin):
    inlines=[
        ProductImagesInline
    ]
class OrderItemsInline(admin.TabularInline):
    model = OrderItem
class OrderAdmin(admin.ModelAdmin):
    inlines=[
        OrderItemsInline
    ]

admin.site.register(Product,ProductAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(Category)
# admin.site.register(Tag)
admin.site.register(ProductAdditionalInfo)
admin.site.register(ProductImages)
admin.site.register(Booking)
admin.site.register(Delivery)
admin.site.register(Table)

