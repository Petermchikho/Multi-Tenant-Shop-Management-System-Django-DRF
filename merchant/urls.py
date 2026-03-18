from django.urls import path
from . views import *
urlpatterns=[
    path('metrics/', MalipoMetricsView.as_view(), name='malipo-metrics'),
    path('merchants/',MerchantListCreateView.as_view()),
    path('merchants/<str:pk>/',MerchantDetailView.as_view()),
    path('shops/',ShopListCreateView.as_view()),
    path('shops/<str:slug>/',ShopDetailView.as_view()),
    path('shops/payment/<str:pk>/',ShopDetailsIDView.as_view()),
    path('shops/<slug:slug>/restore/', ShopRestoreView.as_view(), name='shop-restore'),
    path('shop-types/',ShopTypeListCreateView.as_view()),
    path('shop-types/<str:pk>/',ShopTypeDetailView.as_view()),


    ]