from rest_framework import serializers
from .models import *
from merchant.models import *

class MalipoRequestSerializer(serializers.Serializer):

    merchantTrxId = serializers.CharField()
    customerPhone = serializers.CharField()
    bankId = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class TransactionEnquirySerializer(serializers.Serializer):
    merchantTrxId = serializers.CharField()

class BalanceEnquirySerializer(serializers.Serializer):
    tenant_id = serializers.CharField(required=True)

    def validate(self, data):
        tenant_id = data.get("tenant_id")

        if not tenant_id or not tenant_id.strip():
            raise serializers.ValidationError({"tenant_id": "Tenant ID is required."})

        if not Merchant.objects.filter(id=tenant_id).exists():
            raise serializers.ValidationError({"tenant_id": "Tenant does not exist."})

        return data


class RefundSerializer(serializers.ModelSerializer):
    order_id= serializers.CharField(required=True)
    shop = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(),
        required=True
    )
    class Meta:
        model=MalipoRefund
        exclude=[]

class WithdrawSerializer(serializers.ModelSerializer):
    merchant = serializers.PrimaryKeyRelatedField(
        queryset=Merchant.objects.all(),
        required=True
    )
    class Meta:
        model=MalipoWithdraw
        exclude=[]