from django.urls import path
from . views import *
urlpatterns=[
    path('initiate/',PaymentMalipoInitiate.as_view()),
    path('transaction_enquiry/',TransactionEnquiryMalipo.as_view()),
    path('balance/',MalipoAccountBalance.as_view()),
    path('Refund/',MalipoPaymentRefund.as_view()),
    path('withdraw/',WithdrawAPIView.as_view()),
    path('callbackurl/',CallbackUrlMalipo.as_view()),
]