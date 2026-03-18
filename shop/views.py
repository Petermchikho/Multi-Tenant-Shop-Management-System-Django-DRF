from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAdminUser,AllowAny
from .serializer import *
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import traceback
import json

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from api.pagination import StandardResultsSetPagination
from .utils import *
from django.db.models import Q
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
# Create your views here.

class CategoryCreateListView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=CategorySerializer

    @swagger_auto_schema(
        operation_description="List all categories",
        responses={200: CategorySerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Filter by name", type=openapi.TYPE_STRING)
        ]
    )

    @method_decorator(cache_page(60 * 15,key_prefix='category_list'))
    def get(self,request):
        try:
            categories=Category.objects.all()
            serializer=CategorySerializer(categories,many=True)
            return Response({
                'data': serializer.data,
                'message': 'Categories retrieved successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:

            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
        operation_description="Create a new category",
        request_body=CategoryCreateSerializer,
        responses={201: CategoryCreateSerializer},
        consumes=["multipart/form-data"]
    )

    def post(self,request):
        try:
            data=request.data
            serializer=CategoryCreateSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'data': serializer.data,
                    'message': 'Category created successfully'
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'data': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:

            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)
        
class CategoryDetailView(APIView):

    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=CategoryDetailSerializer

    def get_object(self, slug):
        try:
            return Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        Category = self.get_object(slug)
        serializer = CategoryDetailSerializer(Category)
        return Response({
                'data': serializer.data,
                'message': 'Category retrieved successfully'
            }, status=status.HTTP_200_OK)

    def put(self, request, slug, format=None):
        Category = self.get_object(slug)
        serializer = CategoryCreateSerializer(Category, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            clear_category_cache()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, format=None):
        Category = self.get_object(slug)
        clear_category_cache()
        Category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# class TagCreateListView(APIView):
#     permission_classes=[IsAuthenticatedOrReadOnly]
#     serializer_class=TagSerializer

#     @swagger_auto_schema(
#         operation_description="List all categories",
#         responses={200: TagSerializer(many=True)},
#         manual_parameters=[
#             openapi.Parameter('search', openapi.IN_QUERY, description="Filter by name", type=openapi.TYPE_STRING)
#         ]
#     )

#     def get(self,request):
#         try:
#             tags=Tag.objects.all()
#             serializer=TagSerializer(tags,many=True)
#             return Response({
#                 'data': serializer.data,
#                 'message': 'Tag retrieved successfully'
#             }, status=status.HTTP_200_OK)
#         except Exception as e:

#             return Response({
#                 'data':str(e),
#                 'message':'Something went wrong!'
#             },status=status.HTTP_400_BAD_REQUEST)
        
#     @swagger_auto_schema(
#         operation_description="Create a new Tag",
#         request_body=CategorySerializer,
#         responses={201: CategorySerializer},
#         consumes=["multipart/form-data"]
#     )

#     def post(self,request):
#         try:
#             data=request.data
#             serializer=TagSerializer(data=data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({
#                     'data': serializer.data,
#                     'message': 'Tag created successfully'
#                 }, status=status.HTTP_201_CREATED)
            
#             return Response({
#                 'data': serializer.errors,
#                 'message': 'Validation failed'
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         except Exception as e:

#             return Response({
#                 'data':str(e),
#                 'message':'Something went wrong!'
#             },status=status.HTTP_400_BAD_REQUEST)
        
# class TagDetailView(APIView):

#     permission_classes=[IsAuthenticatedOrReadOnly]
#     serializer_class=TagSerializer

#     def get_object(self, slug):
#         try:
#             return Tag.objects.get(slug=slug)
#         except Tag.DoesNotExist:
#             raise Http404

#     def get(self, request, slug, format=None):
#         tag = self.get_object(slug)
#         serializer = TagSerializer(tag)
#         return Response({
#                 'data': serializer.data,
#                 'message': 'tag retrieved successfully'
#             }, status=status.HTTP_200_OK)

#     def put(self, request, slug, format=None):
#         tag = self.get_object(slug)
#         serializer = TagSerializer(tag, data=request.data,partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, slug, format=None):
#         tag = self.get_object(slug)
#         tag.delete()
#         return Response(status=status.HTTP_200_OK)

class ProductCreateListView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=ProductCreateSerializer

    
    # @method_decorator(vary_on_headers("Authorization"))

    # use this for docs 

    # def get_serializer_class(self):
    #     if self.request.method == 'GET':
    #         return ProductSerializer
    #     return ProductCreateSerializer

    @swagger_auto_schema(
        operation_description="List all Products",
        responses={200: ProductSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Filter by name", type=openapi.TYPE_STRING)
        ]
    )

    # @method_decorator(cache_page(60 * 1,key_prefix='product_list'))
    # @method_decorator(vary_on_cookie)
    # @method_decorator(vary_on_headers("Authorization"))
    def get(self,request):
        try:
            user = request.user
            if user.is_authenticated:
                if user.role == 'vendor':
                    products = Product.objects.filter(shop=user.shop)
                elif user.role == 'super_admin':
                    products = Product.objects.all()
                else:
                    # Other authenticated roles like 'buyer'
                    shop_slug = request.GET.get('shop_slug')
                    if shop_slug:
                        products = Product.objects.filter(shop__slug=shop_slug)
                    else:
                        products = Product.objects.none()
            else:
                # Not authenticated
                shop_slug = request.GET.get('shop_slug')
                if shop_slug:
                    products = Product.objects.filter(shop__slug=shop_slug)
                    
                else:
                    return Response({
                        'data': [],
                        'message': 'shop_slug is required for unauthenticated users'
                    }, status=status.HTTP_400_BAD_REQUEST)
            #apparently we have a bug with the cookies it shows all the products on system failure 
            # ie authentication error   
            if request.GET.get('shop_slug'):
                products = Product.objects.filter(shop__slug=shop_slug)


            
            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(products, request)
            serializer = ProductSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            # serializer=ProductSerializer(products,many=True)
            # return Response({
            #     'data': serializer.data,
            #     'message': 'products retrieved successfully'
            # }, status=status.HTTP_200_OK)
        except Exception as e:

            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
        operation_description="Create a new product",
        request_body=ProductCreateSerializer,
        responses={201: ProductCreateSerializer},
        consumes=["multipart/form-data"]
    )

    def post(self,request):
        try:
            data = request.data
            print(data)
            serializer=ProductCreateSerializer(data=data)
            additional_info_raw = request.data.get('additional_info')
            additional_info = None

            if additional_info_raw:
                try:
                    additional_info = json.loads(additional_info_raw)
                except json.JSONDecodeError:
                    return Response({
                        'message': 'Invalid JSON format for additional_info',
                        'data': {}
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if serializer.is_valid():
                product=serializer.save()
                images_files = request.FILES.getlist('images')
                for img_file in images_files:
                    ProductImages.objects.create(product=product, image=img_file)

                if additional_info:
                    ProductAdditionalInfo.objects.create(product=product, **additional_info)
                response_serializer = ProductCreateSerializer(product)
                return Response({
                    'data': response_serializer.data,
                    'message': 'Product created successfully'
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'data': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            traceback.print_exc()
            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):

    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=ProductCreateSerializer

    def get_object(self, slug):
        try:
            return Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        product = self.get_object(slug)
        serializer = ProductDetailSerializer(product)
        return Response({
                'data': serializer.data,
                'message': 'product retrieved successfully'
            }, status=status.HTTP_200_OK)

    def put(self, request, slug, format=None):
        product = self.get_object(slug)
        serializer = ProductCreateSerializer(product, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, format=None):
        Product = self.get_object(slug)
        Product.delete()
        return Response({'message':'Product deleted'},status=status.HTTP_200_OK)
    


class ProductImagesCreateListView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=ProductImagesCreateSerializer

    # use this for docs 

    # def get_serializer_class(self):
    #     if self.request.method == 'GET':
    #         return ProductSerializer
    #     return ProductCreateSerializer

    @swagger_auto_schema(
        operation_description="List all Product images",
        responses={200: ProductImagesSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Filter by name", type=openapi.TYPE_STRING)
        ]
    )

    def get(self,request):
        try:
            products=ProductImages.objects.all()
            serializer=ProductImagesSerializer(products,many=True)
            return Response({
                'data': serializer.data,
                'message': 'products images retrieved successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:

            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
        operation_description="Create a new image",
        request_body=ProductImagesCreateMultipleSerializer,
        responses={201: ProductImagesCreateMultipleSerializer},
        consumes=["multipart/form-data"]
    )

    def post(self,request):
        try:
            data=request.data
            serializer=ProductImagesCreateMultipleSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'data': serializer.data,
                    'message': 'Product image created successfully'
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'data': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:

            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)


class ProductImageDetailView(APIView):

    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=ProductImagesCreateSerializer

    def get_object(self, pk):
        try:
            return ProductImages.objects.get(pk=pk)
        except ProductImages.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductImagesSerializer(product)
        return Response({
                'data': serializer.data,
                'message': 'product image retrieved successfully'
            }, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductImagesCreateSerializer(product, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        Image = self.get_object(pk)
        Image.delete()
        return Response(status=status.HTTP_200_OK)


class OrderListView(APIView):
    permission_classes=[AllowAny]
    serializer_class=OrderSerialiser
    def get(self,request):

        try:
            search= request.GET.get('search')
            merchant= request.GET.get('tenant')
            shop= request.GET.get('shop')
            statusOrder=request.GET.get('status')
            if not request.user.is_authenticated:
                return Response({'message': 'You are not Authorized'}, status=status.HTTP_401_UNAUTHORIZED)

            if request.user.role == 'super_admin':
                data=Order.objects.all()
            elif request.user.role == 'merchant':
                data=Order.objects.filter(shop__tenant=request.user.merchant)
            elif request.user.role == 'seller':
                data=Order.objects.filter(shop=request.user.shop)
            else:
                return Response({'message': 'You are not Authorized'}, status=status.HTTP_401_UNAUTHORIZED)
            if search:
                data=data.filter(
                    Q(order_id__icontains=search)|
                    Q(first_name__icontains=search)|
                    Q(last_name__icontains=search)|
                    Q(payment_reference__icontains=search)|
                    Q(transaction_id__icontains=search)|
                    Q(shop__tenant__name__icontains=search)|
                    Q(shop__name__icontains=search)|
                    Q(status__icontains=search)
                )
                
            if merchant:
                data=data.filter(
                    Q(shop__tenant__id__icontains=merchant)
                )
            if shop:
                data=data.filter(
                    Q(shop__slug__icontains=shop)
                )
            if statusOrder:
                data=data.filter(
                    Q(status__icontains=statusOrder)
                )
            
            
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            if start_date and end_date:
                data = data.filter(created_at__range=[start_date, end_date])
            elif start_date:
                data = data.filter(created_at__gte=start_date)
            elif end_date:
                data = data.filter(created_at__lte=end_date)

            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(data,request)
            serializer = OrderDetailSerialiser(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
            serializer=OrderDetailSerialiser(data,many=True)
            return Response({
                'data':serializer.data,
                'message':'orders Fetched successfully'
            },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'data':str(e),
                'message':'Something went wrong'
            },status=status.HTTP_400_BAD_REQUEST)
    def post(self,request):
        try:
            data=request.data
            serializer=OrderSerialiser(data=data)
            if not serializer.is_valid():
                return Response({
                    'data':serializer.errors,
                    'message':'Something went wrong'
                },status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                'data':serializer.data,
                'message':'Order Created successfully'
            },status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'data':str(e),
                'message':'Something went wrong'
            },status=status.HTTP_400_BAD_REQUEST)

class OrderDetailView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=OrderUpdateSerialiser

    def get(self,request,pk):
        try:
            data=Order.objects.get(order_id=pk)
            serializer=OrderDetailSerialiser(data)
            return Response({
                'data':serializer.data,
                'message':'orders Fetched successfully'
            },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'data':str(e),
                'message':'Something went wrong'
            },status=status.HTTP_400_BAD_REQUEST)
    def put(self,request,pk):
        try:
            data=Order.objects.get(order_id=pk)
            
            serializer=OrderUpdateSerialiser(instance=data, data=request.data,partial=True)
            if not serializer.is_valid():
                return Response({
                    'data':serializer.errors,
                    'message':'Something went wrong'
                },status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                'data':serializer.data,
                'message':'Category Updated successfully'
            },status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'data':str(e),
                'message':'Something went wrong'
            },status=status.HTTP_400_BAD_REQUEST)

class ProductAdditionInfoCreateListView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=ProductAdditionalInfoCreateSerializer


    def get(self,request):
        try:
            products=ProductAdditionalInfo.objects.all()
            serializer=ProductAdditionalInfoCreateSerializer(products,many=True)
            return Response({
                'data': serializer.data,
                'message': ' additional info retrieved successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:

            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)
        

    def post(self,request):
        try:
            data=request.data
            serializer=ProductAdditionalInfoCreateSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'data': serializer.data,
                    'message': 'addditional info created successfully'
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'data': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:

            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)

class ProductAdditionInfoDetailView(APIView):

    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=ProductAdditionalInfoCreateSerializer

    def get_object(self, pk):
        try:
            return ProductAdditionalInfo.objects.get(pk=pk)
        except ProductAdditionalInfo.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        productInfo = self.get_object(pk)
        serializer = ProductAdditionalInfoCreateSerializer(productInfo)
        return Response({
                'data': serializer.data,
                'message': 'product Info retrieved successfully'
            }, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        productInfo = self.get_object(pk)
        serializer = ProductAdditionalInfoCreateSerializer(productInfo, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        productInfo = self.get_object(pk)
        productInfo.delete()
        return Response(status=status.HTTP_200_OK)
    



class TableCreateListView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=TableCreateSerializer

    @method_decorator(cache_page(60 * 1,key_prefix='table_list'))
    def get(self,request):
        try:
            tables=Table.objects.all()
            
            serializer=TableSerializer(tables,many=True)
            return Response({
                'data': serializer.data,
                'message': 'tables retrieved successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:

            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)


    def post(self,request):
        try:
            data = request.data
            serializer=TableCreateSerializer(data=data)
            if serializer.is_valid():
                table=serializer.save()
                response_serializer = TableCreateSerializer(table)
                return Response({
                    'data': response_serializer.data,
                    'message': 'Table created successfully'
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'data': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            traceback.print_exc()
            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)


class TableDetailView(APIView):

    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=TableCreateSerializer

    def get_object(self, slug):
        try:
            return Table.objects.get(slug=slug)
        except Table.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        table = self.get_object(slug)
        serializer = TableSerializer(table)
        return Response({
                'data': serializer.data,
                'message': 'table retrieved successfully'
            }, status=status.HTTP_200_OK)

    def put(self, request, slug, format=None):
        table = self.get_object(slug)
        serializer = TableCreateSerializer(table, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, format=None):
        table = self.get_object(slug)
        table.delete()
        return Response({'message':'Table deleted'},status=status.HTTP_200_OK)


class BookingCreateListView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=BookingSerializer

    @method_decorator(cache_page(60 * 1,key_prefix='booking_list'))
    def get(self,request):
        try:
            booking=Booking.objects.all()
            
            serializer=BookingSerializer(booking,many=True)
            return Response({
                'data': serializer.data,
                'message': 'booking retrieved successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:

            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)


    def post(self,request):
        try:
            data = request.data
            serializer=BookingSerializer(data=data)
            if serializer.is_valid():
                booking=serializer.save()
                response_serializer = BookingSerializer(booking)
                return Response({
                    'data': response_serializer.data,
                    'message': 'booking created successfully'
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'data': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            traceback.print_exc()
            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)

class BookingDetailView(APIView):

    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=BookingSerializer

    def get_object(self, pk):
        try:
            return Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        booking = self.get_object(pk)
        serializer = BookingDetailsSerializer(booking)
        return Response({
                'data': serializer.data,
                'message': 'table retrieved successfully'
            }, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        booking = self.get_object(pk)
        serializer = BookingSerializer(booking, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        booking = self.get_object(pk)
        booking.delete()
        return Response({'message':'Table deleted'},status=status.HTTP_200_OK)
    


class DeliveryCreateListView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=DeliverySerializer

    @method_decorator(cache_page(60 * 1,key_prefix='booking_list'))
    def get(self,request):
        try:
            data=Delivery.objects.all()
            
            serializer=DeliverySerializer(data,many=True)
            return Response({
                'data': serializer.data,
                'message': 'deliveries retrieved successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:

            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)


    def post(self,request):
        try:
            data = request.data
            serializer=DeliverySerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                
                return Response({
                    'data': serializer.data,
                    'message': 'delivery created successfully'
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'data': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            traceback.print_exc()
            return Response({
                'data':str(e),
                'message':'Something went wrong!'
            },status=status.HTTP_400_BAD_REQUEST)

class DeliveryDetailView(APIView):

    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=DeliverySerializer

    def get_object(self, pk):
        try:
            return Delivery.objects.get(pk=pk)
        except Delivery.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        data = self.get_object(pk)
        serializer =DeliveryDetailsSerializer(data)
        return Response({
                'data': serializer.data,
                'message': 'delivery retrieved successfully'
            }, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        data = self.get_object(pk)
        serializer = DeliverySerializer(data, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        booking = self.get_object(pk)
        booking.delete()
        return Response({'message':'Table deleted'},status=status.HTTP_200_OK)




