from rest_framework import serializers
from .models import *
from shop.models import Order,Product
from payments.models import MalipoRefund
from custom_user.models import User
from authweb.serializers import UserSerializer
from django.db.models import Sum
import qrcode
import base64
from io import BytesIO
from django.conf import settings

class MalipoMetrics(serializers.Serializer):
    amount_made = serializers.SerializerMethodField()
    orders = serializers.SerializerMethodField()
    successful_orders = serializers.SerializerMethodField()
    failed_orders = serializers.SerializerMethodField()
    number_of_merchants = serializers.SerializerMethodField()
    number_of_shops = serializers.SerializerMethodField()  
    refunds = serializers.SerializerMethodField()
    successful_refunds = serializers.SerializerMethodField()
    failed_refunds = serializers.SerializerMethodField()
    refunds_amount=serializers.SerializerMethodField()
    managers=serializers.SerializerMethodField()

    def get_amount_made(self, obj):
        paid_orders = Order.objects.filter(status='paid')
        return sum(order.total_amount for order in paid_orders)

    def get_orders(self, obj):
        return Order.objects.all().count()

    def get_successful_orders(self, obj):
        return Order.objects.filter(status='paid').count()

    def get_failed_orders(self, obj):
        return Order.objects.filter(status='failed').count()
    def get_successful_refunds(self, obj):
        return MalipoRefund.objects.filter(status='success').count()

    def get_failed_refunds(self, obj):
        return MalipoRefund.objects.filter(status='failed').count()

    def get_number_of_merchants(self, obj):
        return Merchant.objects.all().count()

    def get_number_of_shops(self, obj):
        return Shop.objects.all().count()
    def get_refunds(self, obj):
        return MalipoRefund.objects.filter(status='success').count()
    def get_refunds_amount(self, obj):
        refunds = MalipoRefund.objects.filter(order_id__isnull=False)
        return sum(refund.order_id.total_amount for refund in refunds if refund.order_id and refund.status =='success')
    def get_managers(self, obj):
        return User.objects.filter(role='seller').count()


class MerchantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Merchant
        exclude=[]
        read_only_fields = ('created_at', 'updated_at', 'id')

    def validate(self, attrs):
        if not attrs.get('name'):
            raise serializers.ValidationError("Merchant name is required.")
        if not attrs.get('app_id'):
            raise serializers.ValidationError("App ID is required.")
        if not attrs.get('api_key'):
            raise serializers.ValidationError("API key is required.")
        if not attrs.get('email'):
            raise serializers.ValidationError("Email is required.")
        if not attrs.get('phone'):
            raise serializers.ValidationError("Phone number is required.")
        return attrs

class MerchantDetailsSerializer(serializers.ModelSerializer):
    amount_made = serializers.SerializerMethodField()
    shop_count=serializers.SerializerMethodField()
    # shops=serializers.SerializerMethodField()
    orders=serializers.SerializerMethodField()
    successful_orders = serializers.SerializerMethodField()
    failed_orders = serializers.SerializerMethodField()
    refunds = serializers.SerializerMethodField()
    successful_refunds = serializers.SerializerMethodField()
    failed_refunds = serializers.SerializerMethodField()
    refunds_amount=serializers.SerializerMethodField()
    managers=serializers.SerializerMethodField()
    managers_list=serializers.SerializerMethodField()

    class Meta:
        model = Merchant
        exclude = []
        read_only_fields = ('created_at', 'updated_at', 'id')

    def get_amount_made(self, obj):
        orders = Order.objects.filter(shop__tenant=obj, status='paid')
        return sum(order.total_amount for order in orders)
    def get_shop_count(self, obj):
        shops = Shop.objects.filter(tenant=obj).count()
        return shops
    # def get_shops(self, obj):
    #     shops = Shop.objects.filter(tenant=obj)
    #     return ShopSerializer(shops,many=True).data
    def get_orders(self, obj):
        orders = Order.objects.filter(shop__tenant=obj, status='paid').count()
        return orders
    
    def get_successful_orders(self, obj):
        return Order.objects.filter(shop__tenant=obj,status='paid').count()

    def get_failed_orders(self, obj):
        return Order.objects.filter(shop__tenant=obj,status='failed').count()
    def get_refunds(self, obj):
        return MalipoRefund.objects.filter(shop__tenant=obj,status='success').count()
    def get_refunds_amount(self, obj):
        refunds = MalipoRefund.objects.filter(shop__tenant=obj,order_id__isnull=False)
        return sum(refund.order_id.total_amount for refund in refunds if refund.order_id and refund.status =='success')
    def get_managers(self, obj):
        return User.objects.filter(shop__tenant=obj,role='seller').count()
    def get_managers_list(self,obj):
        return UserSerializer(User.objects.filter(shop__tenant=obj,role='seller'),many=True).data
    def get_failed_refunds(self, obj):
        return MalipoRefund.objects.filter(status='failed').count()
    def get_successful_refunds(self, obj):
        return MalipoRefund.objects.filter(status='success').count()

class ShopTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopType
        exclude =[]
        read_only_fields = ('slug',)

class ShopSerializer(serializers.ModelSerializer):
    qr_code = serializers.SerializerMethodField()
    payment_link=serializers.SerializerMethodField()
    amount_made=serializers.SerializerMethodField()
    shop_url=serializers.SerializerMethodField()
    shop_type_name=serializers.SerializerMethodField()
    managers_list=serializers.SerializerMethodField()
    managers=serializers.SerializerMethodField()
    orders=serializers.SerializerMethodField()
    successful_orders = serializers.SerializerMethodField()
    failed_orders = serializers.SerializerMethodField()
    refunds = serializers.SerializerMethodField()
    successful_refunds = serializers.SerializerMethodField()
    failed_refunds = serializers.SerializerMethodField()
    refunds_amount=serializers.SerializerMethodField()
    products=serializers.SerializerMethodField()
    image=serializers.SerializerMethodField()
    logo=serializers.SerializerMethodField()
    
    class Meta:
        model = Shop
        exclude =[]
        read_only_fields = ('slug', 'id')
    
    def get_qr_code(self, obj):
        qr = qrcode.make(f"https://stores.malipo.mw/payment/{obj.id}/")
    
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    def get_payment_link(self,obj):
        return f"https://stores.malipo.mw/payment/{obj.id}/"
    
    def get_amount_made(self, obj):
        orders = Order.objects.filter(shop=obj, status='paid')
        return sum(order.total_amount for order in orders)
    
    def get_shop_url(self,obj):
        shop_base=obj.shop_type.shop_domain
        return f"{shop_base}/{obj.slug}"
    def get_shop_type_name(self,obj):
        shop_name=obj.shop_type.name
        return shop_name
    def get_managers_list(self,obj):
        return UserSerializer(User.objects.filter(shop=obj,role='seller'),many=True).data
    def get_managers(self, obj):
        return User.objects.filter(shop=obj,role='seller').count()
    def get_orders(self, obj):
        orders = Order.objects.filter(shop=obj, status='paid').count()
        return orders
    
    def get_successful_orders(self, obj):
        return Order.objects.filter(shop=obj,status='paid').count()

    def get_failed_orders(self, obj):
        return Order.objects.filter(shop=obj,status='failed').count()
    def get_refunds(self, obj):
        return MalipoRefund.objects.filter(shop=obj,status='success').count()
    def get_refunds_amount(self, obj):
        refunds = MalipoRefund.objects.filter(shop=obj,order_id__isnull=False)
        return sum(refund.order_id.total_amount for refund in refunds if refund.order_id and refund.status =='success')
    def get_failed_refunds(self, obj):
        return MalipoRefund.objects.filter(shop=obj,status='failed').count()
    def get_successful_refunds(self, obj):
        return MalipoRefund.objects.filter(shop=obj,status='success').count()
    def get_products(self, obj):
        return Product.objects.filter(shop=obj).count()
    
    def get_image(self, obj):
        
        if obj.image:
            return settings.SITE_URL + settings.MEDIA_URL + str(obj.image)
            
           
        return None
    def get_logo(self, obj):
        
        if obj.logo:
            return settings.SITE_URL + settings.MEDIA_URL + str(obj.logo)
            
           
        return None

class ShopCreateSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = Shop
        exclude =[]
        read_only_fields = ('slug', 'id')

