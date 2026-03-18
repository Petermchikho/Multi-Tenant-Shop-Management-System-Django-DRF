from rest_framework import serializers
from custom_user.models import User
from django.contrib.auth.password_validation import validate_password
from custom_user.models import Profile
from merchant.models import *

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate_password(self, value):
        validate_password(value)
        return value
class SendOTPResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number=serializers.CharField()
    password = serializers.CharField(write_only=True)
    otp = serializers.CharField()
    role = serializers.CharField()
    merchant = serializers.PrimaryKeyRelatedField(queryset=Merchant.objects.all())
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all(), required=False, allow_null=True)


    def validate_password(self, value):
        validate_password(value)
        return value

class SignupInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number=serializers.CharField()
    role = serializers.CharField()
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all(), required=True)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validate_password(value)
        return value

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validate_password(value)
        return value


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    shop_slug=serializers.SerializerMethodField()
    shop_type=serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude=['password','is_superuser','is_staff','date_joined','groups','user_permissions',]
        

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile fields
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance
    
    def get_shop_slug(self,obj):
        if obj.shop:
            shop_slug=obj.shop.slug
            return shop_slug
        return None
    def get_shop_type(self,obj):
        if obj.shop:
            shop_type=obj.shop.shop_type.name
            return shop_type
        return None

class UserManagersSerializer(serializers.ModelSerializer):
    shop_name=serializers.SerializerMethodField()
   
    class Meta:
        model = User
        exclude=['password','is_superuser','is_staff','date_joined','groups','user_permissions']
    
    def get_shop_name(self,obj):
        shop_name=obj.shop.name
        return shop_name
        