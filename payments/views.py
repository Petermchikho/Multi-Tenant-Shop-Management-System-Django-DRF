from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAdminUser,IsAuthenticated
from .serializers import *
from shop.models import *
from merchant.models import *
from shop.serializer import *
from django.http import Http404
import requests
from .tasks import send_verification_sms_to_shop,send_verification_email
from django.db import transaction

def getHeaders(order_id):
    
    order = Order.objects.get(order_id=order_id) 
    serializer = OrderDetailSerialiser(order)
    data = serializer.data  
    tenant_id = data["shop"]["tenant"]
    tenant = Merchant.objects.get(id=tenant_id)

    # print(tenant.app_id, tenant.api_key)

    
    return {
        'x-app-id': f'{tenant.app_id}',
        'x-api-key': f'{tenant.api_key}',
        'Content-Type': 'application/json'
    } 
def getHeadersByTenantId(tenant_id):
    
    tenant = Merchant.objects.get(id=tenant_id)

    # print(tenant.app_id, tenant.api_key)

    
    return {
        'x-app-id': f'{tenant.app_id}',
        'x-api-key': f'{tenant.api_key}',
        'Content-Type': 'application/json'
    } 


class PaymentMalipoInitiate(APIView):
    serializer_classes=[MalipoRequestSerializer]
    def post(self, request):
        serializer = MalipoRequestSerializer(data=request.data)
        if serializer.is_valid():
            validated = serializer.validated_data

            order_id = validated["merchantTrxId"]

            if Order.objects.filter(order_id=order_id).exists():
                headers = getHeaders(order_id)
            else:
                return Response({"message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
                   
            url = 'https://app.malipo.mw/api/v1/paymentrequest'

            payload = {
                "merchantTrxId": validated["merchantTrxId"],
                "customerPhone": validated["customerPhone"],
                "bankId": validated["bankId"],
                "amount": validated["amount"]
            }

            
            response = requests.post(url, json=payload, headers=headers)

        
            if response.status_code == 201:
                data = response.json()
                return Response({'data':data,}, status=status.HTTP_200_OK)
            else:
                return Response({'response':response.text,'message':"Request failed",'code':response.status_code}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransactionEnquiryMalipo(APIView):
    serializer_class=TransactionEnquirySerializer
    permission_classes=[IsAuthenticated]
    def post(self, request):
        serializer = TransactionEnquirySerializer(data=request.data)
        if serializer.is_valid():
            validated = serializer.validated_data
            order_id = validated["merchantTrxId"]

            if Order.objects.filter(order_id=order_id).exists():
                headers = getHeaders(order_id)
            else:
                return Response({"message": "Order not found."}, status=status.HTTP_404_NOT_FOUND) 
                     
            url = f'https://app.malipo.mw/api/v1/payment/enquire/{validated["merchantTrxId"]}'
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                return Response({'message': 'Verification failed'}, status=status.HTTP_400_BAD_REQUEST)

            data = response.json()
            payment_data = data.get('data', {})
            
            status_text = payment_data.get('status', '')
            amount = float(payment_data.get('amount'))
            currency = payment_data.get('currency')
            payment_reference = payment_data.get("customer_ref")
            transaction_id=payment_data.get("transId")


            try:
                order = Order.objects.get(order_id=validated["merchantTrxId"])
            except Order.DoesNotExist:
                return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

            # Perform validation
            print(order.total_amount)
            if status_text == 'Completed' and currency == 'MWK' and amount >= order.total_amount:
                if order.status != 'paid':  # only run once
                    with transaction.atomic():
                        order.status = 'paid'
                        order.payment_reference = payment_reference
                        order.transaction_id = transaction_id
                        order.save()

                        for item in order.order_items.select_related('product'):
                            product = item.product
                            quantity = item.quantity
                            product.decrease_stock(quantity)
                serializer=OrderDetailSerialiser(order)
                return Response({'data':serializer.data,'message': 'Payment verified and order updated'}, status=status.HTTP_200_OK)
            elif status_text == 'Incomplete':
                order.status = 'pending'
                order.payment_reference=payment_reference
                order.transaction_id=transaction_id
                order.save()
                serializer=OrderDetailSerialiser(order)
                return Response({'data':serializer.data,'message': 'Payment verified and order updated'}, status=status.HTTP_200_OK)
            elif status_text == 'Cancelled':
                order.status = 'cancelled'
                order.payment_reference=payment_reference
                order.transaction_id=transaction_id
                order.save()
                serializer=OrderDetailSerialiser(order)
                return Response({'data':serializer.data,'message': 'Payment verified and order updated'}, status=status.HTTP_200_OK)
            else:
                order.status = 'failed'
                order.payment_reference=payment_reference
                order.transaction_id=transaction_id
                order.save()
                serializer=OrderDetailSerialiser(order)
                return Response({'data':serializer.data,'message': 'Payment Failed and order updated'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MalipoAccountBalance(APIView):
    serializer_class=BalanceEnquirySerializer
    permission_classes=[IsAuthenticated]
    def post(self, request):
        serializer = BalanceEnquirySerializer(data=request.data)
        if serializer.is_valid():
            try:
                validated = serializer.validated_data
                tenant_id = validated["tenant_id"]

                if Merchant.objects.filter(id=tenant_id).exists():
                    headers = getHeadersByTenantId(tenant_id)
                else:
                    return Response({"message": "Merchant not found."}, status=status.HTTP_404_NOT_FOUND)
                url = f'https://app.malipo.mw/api/v1/accounts/balance'
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    return Response({'message': 'Verification failed'}, status=status.HTTP_400_BAD_REQUEST)

                data = response.json()
                balance = data.get('data', {})
                return Response({'data':balance,}, status=status.HTTP_200_OK)
                
            except Exception as e:

                return Response({
                    'data':str(e),
                    'message':'Something went wrong!'
                },status=status.HTTP_400_BAD_REQUEST)     
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    

class MalipoPaymentRefund(APIView):
      serializer_class=RefundSerializer
      permission_classes=[IsAuthenticated]

      def post(self,request):
          try:
              serializer = RefundSerializer(data=request.data)
              if serializer.is_valid():
                  validated_data = serializer.validated_data
                  transaction_id = validated_data["transaction_id"] 
                  order_id = validated_data["order_id"]  
                  if Order.objects.filter(order_id=order_id).exists():
                        headers = getHeaders(order_id)
                  else:
                        return Response({"message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)  
                  url = f'https://app.malipo.mw/api/v1/payment/refund/{transaction_id}'

                  response = requests.post(url, headers=headers,timeout=10)
                  print(response.status_code)
                  print(response.text)
                  print(response.json())
                  print(url)

                  if response.status_code == 200:
                        data = response.json()
                        refund_instance = serializer.save(
                            status=data.get("status"),
                            reversal_trans_id=data.get("reversal_trans_id"),
                            customer_ref=data.get("customer_ref")
                        )
                        return Response({
                            "message": "Refund processed successfully",
                            "refund": RefundSerializer(refund_instance).data
                        }, status=200)
                  else:
                        return Response({'response':response.text,'message':"Request failed",'code':response.status_code}, status=status.HTTP_200_OK)
              return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                  

          except Exception as e:
              return Response({
                    'data':str(e),
                    'message':'Something went wrong!'
                },status=status.HTTP_400_BAD_REQUEST)   

    
class WithdrawAPIView(APIView):
    serializer_classes=[WithdrawSerializer]
    def post(self, request):
        serializer = WithdrawSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            merchantTrxId = instance.withdraw_id   
            wallet=instance.customerPhone
            bankId=instance.bankId   
            amount=instance.amount         
            url = 'https://app.malipo.mw/api/v1/payments/withdrawal'

            payload = {
                "merchantTrxId": f'{merchantTrxId}',
                "wallet": f'{wallet}',
                "bankId": bankId,
                "amount": amount
            }

            response = requests.post(url, json=payload, headers=headers)

        
            if response.status_code == 201:
                data = response.json()

     
                txn_data = data.get("data", {})
                instance.account_number = txn_data.get("account_number")
                instance.transaction_id = txn_data.get("transaction_id")
                instance.transaction_type_id = txn_data.get("transaction_type_id")
                instance.save()

                        
                return Response({'data':data,'message':"Withdrawal successful"}, status=status.HTTP_200_OK)
            else:
                return Response({'response':response.text,'message':"Request failed",'code':response.status_code}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class CallbackUrlMalipo(APIView):
    
    def post(self, request):
        data= request.data
        if request.data:
            
            order_id = data.get('merchant_txn_id')
            status_text = data.get('status', '')
            amount = float(data.get('amount'))
            payment_reference = data.get("customer_ref")
            transaction_id=data.get("transaction_id")
            
            try:
                order = Order.objects.get(order_id=order_id)
            except Order.DoesNotExist:
                return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

            
            if status_text == 'Completed' and amount >= order.total_amount:
                if order.status != 'paid':  # only run once
                    with transaction.atomic():
                        order.status = 'paid'
                        order.payment_reference = payment_reference
                        order.transaction_id = transaction_id
                        order.save()

                        for item in order.order_items.select_related('product'):
                            product = item.product
                            quantity = item.quantity
                            product.decrease_stock(quantity)
                serializer=OrderDetailSerialiser(order)
                message = (
                    f"Hello {order.shop.name} manager,\n\n"
                    f"Your account has been credited with MKW {amount} \n"
                    
                    "Please log in to https://stores.malipo.mw and check on all your transactions later on.\n"
                    "- Malawi Stores Team"
                )
                send_verification_sms_to_shop.delay('Matikiti', order.shop.phone, message)
                send_verification_email.delay(order.shop.email,message)
                return Response({'data':serializer.data,'message': 'Payment verified and order updated'}, status=status.HTTP_200_OK)
            elif status_text == 'Incomplete':
                order.status = 'pending'
                order.payment_reference=payment_reference
                order.transaction_id=transaction_id
                order.save()
                serializer=OrderDetailSerialiser(order)
                return Response({'data':serializer.data,'message': 'Payment verified and order updated'}, status=status.HTTP_200_OK)
            elif status_text == 'Cancelled':
                order.status = 'cancelled'
                order.payment_reference=payment_reference
                order.transaction_id=transaction_id
                order.save()
                serializer=OrderDetailSerialiser(order)
                return Response({'data':serializer.data,'message': 'Payment verified and order updated'}, status=status.HTTP_200_OK)
            else:
                order.status = 'failed'
                order.payment_reference=payment_reference
                order.transaction_id=transaction_id
                order.save()
                serializer=OrderDetailSerialiser(order)
                return Response({'data':serializer.data,'message': 'Payment Failed and order updated'}, status=status.HTTP_200_OK)
        
        return Response({'message':'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

          