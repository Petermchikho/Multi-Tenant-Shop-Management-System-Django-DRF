from django.urls import path
from . views import *
urlpatterns=[
    path('categories/',CategoryCreateListView.as_view()),
    path('categories/<str:slug>/',CategoryDetailView.as_view()),
    # path('tags/',TagCreateListView.as_view()),
    # path('tags/<str:slug>/',TagDetailView.as_view()),
    path('tables/',TableCreateListView.as_view()),
    path('tables/<str:slug>/',TableDetailView.as_view()),
    path('bookings/',BookingCreateListView.as_view()),
    path('bookings/<str:pk>/',BookingDetailView.as_view()),
    path('deliveries/',DeliveryCreateListView.as_view()),
    path('deliveries/<str:pk>/',DeliveryDetailView.as_view()),
    path('products/',ProductCreateListView.as_view()),
    path('products-additional-info/',ProductAdditionInfoCreateListView.as_view()),
    path('products-additional-info/<str:pk>/',ProductAdditionInfoDetailView.as_view()),
    path('products/<str:slug>/',ProductDetailView.as_view()),
    path('products/detail/images/',ProductImagesCreateListView.as_view()),
    path('products/images/<str:pk>/',ProductImageDetailView.as_view()),
    path('order/',OrderListView.as_view()),
    path('order/<str:pk>/',OrderDetailView.as_view()),
    
    ]