from rest_framework import serializers
from .models import *
from django.conf import settings
from django.db import transaction
from merchant.models import *

# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Tag
#         exclude=[]
#         extra_kwargs = {
#             'id': {'read_only': True},
#             'slug': {'read_only': True},
#         }


class CategorySerializer(serializers.ModelSerializer):
    count=serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    class Meta:
        model=Category
        exclude=[]
        extra_kwargs = {
            'id': {'read_only': True},
            'slug': {'read_only': True},
        }
    

    def get_count(self,obj):
        data=Product.objects.filter(category=obj)
        return data.count()
    
    def get_image(self, obj):
        
        if obj.image:
            return settings.SITE_URL + settings.MEDIA_URL + str(obj.image)
 
        return None
class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        exclude=[]
        extra_kwargs = {
            'id': {'read_only': True},
            'slug': {'read_only': True},
        }

class ProductAdditionalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductAdditionalInfo
        exclude = ['product']
class ProductAdditionalInfoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductAdditionalInfo
        exclude = []

class ProductImagesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model=ProductImages
        exclude=[]

    def get_image(self, obj):
        
        if obj.image:
            return settings.SITE_URL + settings.MEDIA_URL + str(obj.image)
            
           
        return None
    
class ProductImagesCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=ProductImages
        exclude=['product']
class ProductImagesCreateMultipleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=ProductImages
        exclude=[]


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model=Product
        exclude=[]
        depth=1
        extra_kwargs = {
            'id': {'read_only': True},
            'slug': {'read_only': True},
        }

    def get_image(self, obj):
        
        if obj.image:
            return settings.SITE_URL + settings.MEDIA_URL + str(obj.image)
            
           
        return None
    
class ProductDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    related_products=serializers.SerializerMethodField()
    additional_info=serializers.SerializerMethodField()
    shop_type_name=serializers.SerializerMethodField()
    class Meta:
        model=Product
        exclude=[]
        depth=1
        extra_kwargs = {
            'id': {'read_only': True},
            'slug': {'read_only': True},
        }

    def get_related_products(self, obj):
        related_products = Product.objects.filter(category=obj.category).exclude(id=obj.id)[:6]
        return ProductSerializer(related_products, many=True).data
    def get_shop_type_name(self, obj):
        return obj.shop.shop_type.name
    def get_additional_info(self, obj):
        try:
            additional_info = ProductAdditionalInfo.objects.get(product=obj)
            return ProductAdditionalInfoSerializer(additional_info).data
        except ProductAdditionalInfo.DoesNotExist:
            return None
    
    def get_images(self, obj):
        images = ProductImages.objects.filter(product=obj)
        return ProductImagesSerializer(images, many=True).data
    
    def get_image(self, obj):
        
        if obj.image:
            return settings.SITE_URL + settings.MEDIA_URL + str(obj.image)
            
           
        return None
    
class ProductCreateSerializer(serializers.ModelSerializer):
    additional_info = ProductAdditionalInfoSerializer(required=False)
    images= ProductImagesCreateSerializer(many=True,required=False)
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all())
    class Meta:
        model=Product
        exclude=[]
        extra_kwargs = {
            'id': {'read_only': True},
            'slug': {'read_only': True},
            # 'shop': {'read_only': True},  # Assuming shop is set automatically
        }
    
    
    def create(self, validated_data):
        #just pass the data without the product id
           
        # tags = validated_data.pop('tags', [])
        

        # Create the product
        product = Product.objects.create(**validated_data)

        # Assign many-to-many tags
        # product.tags.set(tags)


        return product




class CategoryDetailSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    class Meta:
        model=Category
        exclude=[]
        extra_kwargs = {
            'id': {'read_only': True},
            'slug': {'read_only': True},
        }

    def get_products(self,obj):
        data=Product.objects.filter(category=obj)
        return ProductSerializer(data,many=True).data
    
    def get_image(self, obj):
        
        if obj.image:
            return settings.SITE_URL + settings.MEDIA_URL + str(obj.image)
            
        return None
    

class OrderItemSerializer(serializers.ModelSerializer):
    item_subtotal = serializers.SerializerMethodField()
    
    order=serializers.CharField(required=False)
    class Meta:
        model=OrderItem
        exclude=[]
    def get_item_subtotal(self, obj):
        return obj.product.final_price * obj.quantity

class ProductDetailOrderSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
        
    class Meta:
        model=Product
        exclude=[]
        extra_kwargs = {
            'id': {'read_only': True},
            'slug': {'read_only': True},
        }
    
    
    def get_image(self, obj):
        
        if obj.image:
            return settings.SITE_URL + settings.MEDIA_URL + str(obj.image)
            
           
        return None

class OrderItemDetailSerializer(serializers.ModelSerializer):
    item_subtotal = serializers.SerializerMethodField()
    product=ProductDetailOrderSerializer()
    order=serializers.CharField(required=False)
    class Meta:
        model=OrderItem
        exclude=[]
        depth=2
    def get_item_subtotal(self, obj):
        return obj.product.final_price * obj.quantity
       


class OrderSerialiser(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, required=False)
    total_amount = serializers.SerializerMethodField()
    app_id=serializers.SerializerMethodField()

    class Meta:
        model = Order
        exclude = []

    def validate(self, attrs):
        order_items = self.initial_data.get('order_items')
        custom_amount = attrs.get('custom_amount')

        if not order_items and not custom_amount:
            raise serializers.ValidationError("Provide either order_items or custom_amount.")

        booking_status = attrs.get('booking_status')
        table = attrs.get('table')
        date = attrs.get('date')
        start_time = attrs.get('time')  # assuming time is start_time

        if booking_status == 'yes' and table and date and start_time:
            # Calculate end_time as 1 hour after start_time
            start_dt = datetime.combine(date, start_time)
            end_dt = start_dt + timedelta(hours=1)
            end_time = end_dt.time()

            # 👇 Check overlapping bookings for a single table
            overlapping_bookings = Booking.objects.filter(
                table=table,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            if overlapping_bookings.exists():
                raise serializers.ValidationError(
                    f"Table {table.id} is already booked during the selected time slot."
                )

        return attrs

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items', None)
        booking_status = validated_data.get('booking_status')
        delivery_status = validated_data.get('delivery_status')
        table = validated_data.pop('table', None)

        booking_fields = {
            'first_name': validated_data.get('first_name'),
            'last_name': validated_data.get('last_name'),
            'phone': validated_data.get('phone'),
            'email': validated_data.get('email'),
            'date': validated_data.get('date'),
            'start_time': validated_data.get('time'),
        }

        delivery_fields = {
            'first_name': validated_data.get('first_name'),
            'last_name': validated_data.get('last_name'),
            'phone': validated_data.get('phone'),
            'email': validated_data.get('email'),
            'time': validated_data.get('time'),
            'location': validated_data.get('location'),
        }

        # order = Order.objects.create(**validated_data)

        # if order_items_data:
        #     for item_data in order_items_data:
        #         OrderItem.objects.create(order=order, **item_data)
        
        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            if order_items_data:
                for item_data in order_items_data:
                    product = item_data['product']
                    quantity = item_data.get('quantity', 1)

                    # Reduce stock if applicable
                    product = Product.objects.get(id=product.id)
                    # product.decrease_stock(quantity)

                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity
                    )

        if booking_status == 'yes' and table:
            
            Booking.objects.create(
                order=order,
                table=table,
                **booking_fields
            )

        if delivery_status == 'yes':
            
            Delivery.objects.create(
                order=order,
                **delivery_fields
            )

        

        return order

    def get_total_amount(self, order):
        if order.order_items.exists():
            print(sum((item.product.final_price) * item.quantity for item in order.order_items.all()))
            return sum((item.product.final_price) * item.quantity for item in order.order_items.all())
        return order.custom_amount or 0
    def get_app_id(self, obj):
        if obj.shop and obj.shop.tenant:
            return obj.shop.tenant.app_id
        return None
    
class OrderUpdateSerialiser(serializers.ModelSerializer):

    class Meta:
        model=Order
        exclude=[]

class OrderDetailSerialiser(serializers.ModelSerializer):
    order_items = OrderItemDetailSerializer(many=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model=Order
        exclude=[]
        depth=1
    
    
    
    def get_total_amount(self, order):
        if order.order_items.exists():
            return sum(item.product.final_price * item.quantity for item in order.order_items.all())
        return order.custom_amount or 0
    
class TableCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Table
        exclude=[]
        extra_kwargs = {
            'id': {'read_only': True},
            'slug': {'read_only': True},
            'booked': {'read_only': True},
        }

class TableSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model=Table
        exclude=[]
        
    
    def get_image(self, obj):
        
        if obj.image:
            return settings.SITE_URL + settings.MEDIA_URL + str(obj.image)
            
           
        return None



class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model=Booking
        exclude=[]
        
class BookingDetailsSerializer(serializers.ModelSerializer):
    order=OrderDetailSerialiser(read_only=True)
    class Meta:
        model=Booking
        exclude=[]
        depth=1

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model=Delivery
        exclude=[]
        
class DeliveryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Delivery
        exclude=[]
        depth=1
        

# {
#     "merchantTrxId":"E6B5CEBF3099",
#     "customerPhone": "265998671706",
#     "bankId": 1,
#     "amount":190
# }