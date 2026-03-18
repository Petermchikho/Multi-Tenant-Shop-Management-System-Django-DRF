from django.db import models
import uuid
from merchant.models import *
from shop.models import Order


def generate_order_id():
    return str(uuid.uuid4()).replace('-', '').upper()[:12]

STATUS=(
    ('failed','failed'),
    ('success','success')
)

class MalipoRefund(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='refunds')
    transaction_id=models.CharField(max_length=200)
    shop=models.ForeignKey(Shop,related_name='shop',on_delete=models.SET_NULL,null=True,blank=True)
    reversal_trans_id=models.CharField(max_length=200,null=True,blank=True)
    customer_ref=models.CharField(max_length=200,null=True,blank=True)
    status=models.CharField(max_length=200,choices=STATUS,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id}-{self.status}"



class MalipoWithdraw(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='withdraws',null=True,blank=True)
    withdraw_id = models.CharField(max_length=20,primary_key=True, unique=True, default=generate_order_id)
    transaction_id=models.CharField(max_length=200,null=True,blank=True)
    account_number=models.CharField(max_length=200,null=True,blank=True)
    customerPhone=models.CharField(max_length=200)
    transaction_type_id=models.CharField(max_length=200,null=True,blank=True)
    bankId=models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.withdraw_id}-{self.customerPhone}"
    