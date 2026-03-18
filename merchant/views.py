
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import Merchant
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import traceback
import json

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from api.pagination import StandardResultsSetPagination
from django.db.models import Q
from api.pagination import StandardResultsSetPagination

from rest_framework.permissions import IsAdminUser, SAFE_METHODS,IsAuthenticatedOrReadOnly, IsAuthenticated

class IsAdminForGETAllowAllForPOST(IsAdminUser):
    """
    - GET: only admin users
    - POST: allow everyone
    - Other methods: fallback to IsAdminUser
    """

    def has_permission(self, request, view):
        if request.method == 'GET':
            return super().has_permission(request, view)  # only admin
        elif request.method == 'POST':
            return True  # allow anyone to create
        else:
            return super().has_permission(request, view)  # only admin for other methods
        
class IsAdminForPOSTAllowAllForGET(IsAdminUser):
    """
    - GET: only admin users
    - POST: allow everyone
    - Other methods: fallback to IsAdminUser
    """

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True 
        elif request.method == 'POST':
            return super().has_permission(request, view)
        else:
            return super().has_permission(request, view)  # only admin for other methods

class MalipoMetricsView(APIView):
    permission_classes = [IsAdminUser]  

    def get(self, request, *args, **kwargs):
        serializer = MalipoMetrics(instance={})
        return Response(serializer.data)
    
class MerchantListCreateView(APIView):
    permission_classes = [IsAdminForGETAllowAllForPOST]

    @swagger_auto_schema(
        operation_description="List all merchants or create a new merchant",
        responses={
            200: MerchantSerializer(many=True),
            201: MerchantSerializer,
            400: "Bad Request"
        }
    )
    def get(self, request):
        try:
            search= request.GET.get('search')
            merchants = Merchant.objects.all()

            if search:
                merchants=merchants.filter(
                    Q(id__icontains=search)|
                    Q(app_id__icontains=search)|
                    Q(email__icontains=search)|
                    Q(phone__icontains=search)|
                    Q(district__icontains=search)|
                    Q(address__icontains=search)|
                    Q(district__icontains=search)|
                    Q(name__icontains=search)
                )
                 
            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(merchants, request)
            serializer = MerchantDetailsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
            # serializer = MerchantDetailsSerializer(merchants, many=True)
            # return Response({
            #         'data': serializer.data,
            #         'message': 'Merchants retrieved successfully'
            #     }, status=status.HTTP_200_OK)
        
        except Exception as e:

            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Create a new merchant",
        request_body=MerchantSerializer,
        responses={
            201: MerchantSerializer,
            400: "Bad Request"
        }
    )
    def post(self, request):
        try:
            serializer = MerchantSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:

            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)

class MerchantDetailView(APIView):
    permission_classes = [IsAdminForPOSTAllowAllForGET]

    @swagger_auto_schema(
        operation_description="Retrieve, update or delete a merchant by ID",
        responses={
            200: MerchantSerializer,
            404: "Merchant not found",
            400: "Bad Request"
        }
    )
    def get(self, request, pk):
        try:
            user = request.user

            if user.role == 'super_admin':
                merchant = Merchant.objects.get(pk=pk)

            elif hasattr(user, 'merchant') and str(user.merchant.id) == str(pk):
                merchant = user.merchant

            else:
                return Response({'detail': 'Unauthorized access'}, status=403)


            serializer = MerchantDetailsSerializer(merchant)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Merchant.DoesNotExist:
            return Response({'message': 'Merchant not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Update a merchant by ID",
        request_body=MerchantSerializer,
        responses={
            200: MerchantSerializer,
            404: "Merchant not found",
            400: "Bad Request"
        }
    )
    def put(self, request, pk):
        try:
            merchant = Merchant.objects.get(pk=pk)
            serializer = MerchantSerializer(merchant, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Merchant.DoesNotExist:
            return Response({'message': 'Merchant not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a merchant by ID",
        responses={
            204: "No Content",
            404: "Merchant not found"
        }
    )
    def delete(self, request, pk):
        try:
            merchant = Merchant.objects.get(pk=pk)
            merchant.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Merchant.DoesNotExist:
            return Response({'message': 'Merchant not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ShopTypeListCreateView(APIView):
    permission_classes = [IsAdminForPOSTAllowAllForGET]

    @swagger_auto_schema(
        operation_description="List all shop types or create a new shop type",
        responses={
            200: ShopTypeSerializer(many=True),
            201: ShopTypeSerializer,
            400: "Bad Request"
        }
    )
    def get(self, request):
        try:
            shop_types = ShopType.objects.all()
            serializer = ShopTypeSerializer(shop_types, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Create a new shop type",
        request_body=ShopTypeSerializer,
        responses={
            201: ShopTypeSerializer,
            400: "Bad Request"
        }
    )
    def post(self, request):
        try:
            serializer = ShopTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ShopTypeDetailView(APIView):
    permission_classes = [IsAdminForPOSTAllowAllForGET]

    @swagger_auto_schema(
        operation_description="Retrieve, update or delete a shop type by ID",
        responses={
            200: ShopTypeSerializer,
            404: "Shop Type not found",
            400: "Bad Request"
        }
    )
    def get(self, request, pk):
        try:
            shop_type = ShopType.objects.get(pk=pk)
            serializer = ShopTypeSerializer(shop_type)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ShopType.DoesNotExist:
            return Response({'message': 'Shop Type not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Update a shop type by ID",
        request_body=ShopTypeSerializer,
        responses={
            200: ShopTypeSerializer,
            404: "Shop Type not found",
            400: "Bad Request"
        }
    )
    def put(self, request, pk):
        try:
            shop_type = ShopType.objects.get(pk=pk)
            serializer = ShopTypeSerializer(shop_type, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except ShopType.DoesNotExist:
            return Response({'message': 'Shop Type not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a shop type by ID",
        responses={
            204: "No Content",
            404: "Shop Type not found"
        }
    )
    def delete(self, request, pk):
        try:
            shop_type = ShopType.objects.get(pk=pk)
            shop_type.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except ShopType.DoesNotExist:
            return Response({'message': 'Shop Type not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class ShopListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="List all shops or create a new shop",
        responses={
            200: ShopSerializer(many=True),
            201: ShopSerializer,
            400: "Bad Request",
            401:"Only merchants can add shops"
        }
    )
    def get(self, request):
        try:
            search= request.GET.get('search')
            merchant= request.GET.get('merchant')
            if request.user.is_authenticated:
                if request.user.role == 'seller':
                    shops=Shop.objects.filter(id=request.user.shop)
                elif request.user.role == 'merchant':
                    shops=Shop.objects.filter(tenant=request.user.merchant)
                else:
                    shops = Shop.objects.all()
            else:
                shops = Shop.objects.all()
            
            if search:
                shops=shops.filter(
                    Q(name__icontains=search)|
                    Q(shop_type__name__icontains=search)|
                    Q(location__icontains=search)|
                    Q(address__icontains=search)|
                    Q(tenant__id__icontains=search)
                )
            if merchant:
                shops=shops.filter(
                    Q(tenant__id__icontains=merchant)
                )


            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(shops, request)
            serializer = ShopSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
            # serializer = ShopSerializer(shops, many=True)
            # return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Create a new shop",
        request_body=ShopSerializer,
        responses={
            201: ShopSerializer,
            400: "Bad Request"
        }
    )
    def post(self, request):
        try:
            if request.user.role != 'merchant':
                return Response({'message':'Only a merchant can add a shop'}, status=status.HTTP_401_UNAUTHORIZED)
            serializer = ShopCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ShopDetailsIDView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Retrieve, update or delete a shop by ID",
        responses={
            200: ShopSerializer,
            404: "Shop not found",
            400: "Bad Request"
        }
    )
    def get(self, request, pk):
        try:
            shop = Shop.objects.get(pk=pk)
            serializer = ShopSerializer(shop)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Shop.DoesNotExist:
            return Response({'message': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ShopDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Retrieve, update or delete a shop by ID",
        responses={
            200: ShopSerializer,
            404: "Shop not found",
            400: "Bad Request"
        }
    )
    def get(self, request, slug):
        try:
            shop = Shop.objects.get(slug=slug)
            serializer = ShopSerializer(shop)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Shop.DoesNotExist:
            return Response({'message': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Update a shop by ID",
        request_body=ShopSerializer,
        responses={
            200: ShopSerializer,
            404: "Shop not found",
            400: "Bad Request"
        }
    )
    def put(self, request, slug):
        try:
            shop = Shop.objects.get(slug=slug)
            serializer = ShopSerializer(shop, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Shop.DoesNotExist:
            return Response({'message': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a shop by ID",
        responses={
            204: "No Content",
            404: "Shop not found"
        }
    )
    def delete(self, request, slug):
        try:
            shop = Shop.objects.get(slug=slug)
            shop.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Shop.DoesNotExist:
            return Response({'message': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class ShopRestoreView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Restore a soft-deleted shop by slug",
        responses={
            200: ShopSerializer,
            404: "Shop not found or already active",
            400: "Bad request"
        }
    )
    def post(self, request, slug):
        try:
            shop = Shop.all_objects.get(slug=slug, status='inactive')
            shop.restore()
            serializer = ShopSerializer(shop)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Shop.DoesNotExist:
            return Response({'message': 'Shop not found or already active'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)