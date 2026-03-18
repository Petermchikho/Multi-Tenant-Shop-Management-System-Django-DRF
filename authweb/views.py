from django.contrib.auth import authenticate,login
from custom_user.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import EmailOTP
from .serializers import *
from django.core.mail import send_mail
import random
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from .utils import get_id_token_with_code_method_1,get_id_token_with_code_method_2
from .tasks import send_otp_email,send_sms,send_invite_sms
from api.pagination import StandardResultsSetPagination

from django.utils.crypto import get_random_string
from django.db.models import Q

#authentication_classes = [JWTAuthentication]

# Cookie setter function
def set_cookie_tokens(response, user):
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    if settings.DEBUG:
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production (requires HTTPS)
            samesite='Lax',
            path='/',
            max_age=60 * 60 * 24  # 1 day
        )

        # Refresh token (longer-lived)
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=False,  # Set to True in production
            samesite='Lax',
            path='/',
            max_age=60 * 60 * 24 * 30  # 30 days
        )
    else:
        # Access token (short-lived)
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,  # Set to True in production (requires HTTPS)
            samesite='None',
            path='/',
            max_age=60 * 60 * 24  # 1 day
        )

        # Refresh token (longer-lived)
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,  # Set to True in production
            samesite='None',
            path='/',
            max_age=60 * 60 * 24 * 30  # 30 days
        )


class SendOTPView(APIView):
    def post(self, request):
        #send the otp to the user email for before creating account
        #Note to self it expires after 5 minutes add in email template
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        phone = serializer.validated_data['phone_number']

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists for another user!'}, status=400)

        otp = str(random.randint(100000, 999999))
        otp_hash = EmailOTP.hash_otp(otp)
        #if an OTP exists already delete it 
        EmailOTP.objects.filter(email=email).delete()
        EmailOTP.objects.create(email=email, otp_hash=otp_hash)
        send_otp_email.delay(otp,email)
        message = f'Your OTP for Account Verification is {otp}'
        send_sms.delay('Matikiti', phone, message)
        # send_mail('Your OTP', f'Your OTP is {otp}', 'info@mobipay.mw', [email])
        return Response({'message': 'OTP sent'})
    
class SendOTPResetView(APIView):
    def post(self, request):
        serializer = SendOTPResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        if not User.objects.filter(email=email).exists():
            return Response({'error': 'User does not exists'}, status=400)

        otp = str(random.randint(100000, 999999))
        otp_hash = EmailOTP.hash_otp(otp)
        EmailOTP.objects.filter(email=email).delete()
        EmailOTP.objects.create(email=email, otp_hash=otp_hash)
        send_mail('Your OTP', f'Your Reset password OTP is {otp}', 'info@mobipay.mw', [email])
        return Response({'message': 'OTP sent'})

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        if User.objects.filter(email=email).exists():
            return Response({'error': 'User already exists'}, status=400)
        otp_hash = EmailOTP.hash_otp(otp)
        otp_obj = EmailOTP.objects.filter(email=email, otp_hash=otp_hash).last()
        if not otp_obj or otp_obj.is_expired():
            return Response({'error': 'Invalid or expired OTP'}, status=400)

        # user = User.objects.create_user(
        #     email=email,
        #     password=serializer.validated_data['password'],
        #     first_name = serializer.validated_data['first_name'],
        #     last_name = serializer.validated_data['last_name'],
        #     phone_number=serializer.validated_data['phone_number'],
        #     role=serializer.validated_data['role'],
        #     merchant=serializer.validated_data['merchant'],
        # )
        user_data = {
            "email": email,
            "password": serializer.validated_data['password'],
            "first_name": serializer.validated_data['first_name'],
            "last_name": serializer.validated_data['last_name'],
            "phone_number": serializer.validated_data['phone_number'],
            "role": serializer.validated_data['role'],
            "merchant": serializer.validated_data['merchant'],
        }

        # Add shop only if it's provided
        if 'shop' in serializer.validated_data:
            user_data['shop'] = serializer.validated_data['shop']

        # Create the user
        user = User.objects.create_user(**user_data)

        response = Response({'message': 'Signup successful'})
        set_cookie_tokens(response, user)
        return response

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class LoginView(APIView):
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        if user is not None:
           login(request, user)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=400)
        response = Response({'message': 'Login successful'})
        set_cookie_tokens(response, user)
        return response



class Login2FAView(APIView):
    def post(self, request):
        # Validate the credentials (email and password)
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Authenticate the user
        user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        if user is not None:
           login(request, user)
        
        if not user:
            return Response({'error': 'Invalid credentials'}, status=400)
        
        # Check if the OTP has already been sent for this email
        otp = str(random.randint(100000, 999999))  # Generate OTP
        otp_hash = EmailOTP.hash_otp(otp)
        EmailOTP.objects.filter(email=user.email).delete()
        # Save OTP in the database
        EmailOTP.objects.create(email=user.email, otp_hash=otp_hash)
        
        # Send the OTP to the user's email
        send_mail('Your OTP', f'Your OTP is {otp}', 'info@mobipay.mw', [user.email])

        # In this case, we’re sending a message asking for the OTP.
        return Response({'message': 'OTP sent to email. Please verify OTP.'})

class VerifyOTP2FAView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Hash the entered OTP and retrieve the stored OTP object
        otp_hash = EmailOTP.hash_otp(serializer.validated_data['otp'])
        otp_obj = EmailOTP.objects.filter(
            email=serializer.validated_data['email'],
            otp_hash=otp_hash
        ).last()

        # If the OTP does not exist or has expired
        if not otp_obj or otp_obj.is_expired():
            return Response({'error': 'Invalid or expired OTP'}, status=400)
        
        # After successful OTP verification, create JWT tokens for the user
        user = User.objects.get(email=serializer.validated_data['email'])
        response = Response({'message': 'OTP verified. You are now logged in.'})
        set_cookie_tokens(response, user)  # Set tokens as cookies
        
        # Optionally, delete the OTP after successful verification for security
        otp_obj.delete()
        
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token', None)

        if refresh_token is None:
            return Response({'error': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({'message': 'Token refreshed'})
            if settings.DEBUG:
                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=True,
                    secure=False,  # Set to True in production
                    samesite='Lax',
                    max_age=60 * 60 * 24  # 1 day
                )
            else:
                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=True,
                    secure=True,  # Set to True in production
                    samesite='None',
                    max_age=60 * 60 * 24  # 1 day
                )
            return response

        except TokenError:
            response = Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response
        
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception as e:
            print("Logout blacklist error:", str(e)) 

        response = Response({'message': 'Logged out'})
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        return response


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Incorrect old password'}, status=400)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed'})


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email=serializer.validated_data['email']
        otp=serializer.validated_data['otp']
        otp_hash = EmailOTP.hash_otp(otp)
        otp_obj = EmailOTP.objects.filter(email=email, otp_hash=otp_hash).last()
       
        if not otp_obj or otp_obj.is_expired():
            return Response({'error': 'Invalid or expired OTP'}, status=400)

        user = User.objects.filter(email=serializer.validated_data['email']).first()
        if not user:
            return Response({'error': 'User not found'}, status=404)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password reset successful'})

def authenticate_or_create_user(email):
    try: 
        user=User.objects.get(email=email)
    except User.DoesNotExist:
        # user=User.objects.create_user(email=email)
        raise 
    return user
class LoginWithGoogle(APIView):
    def post(self,request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Missing authorization code'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            id_token = get_id_token_with_code_method_2(code)
            user_email = id_token['email']
            user = authenticate_or_create_user(user_email)
            if user is not None:
               login(request, user)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'error': 'Invalid Google code or token'}, status=status.HTTP_400_BAD_REQUEST)

        response = Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        set_cookie_tokens(response, user)
        return response


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class InviteUserView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = SignupInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        if User.objects.filter(email=email).exists():
            return Response({'error': 'User already exists'}, status=400)
        password = get_random_string(length=8)

        user_data = {
            "email": email,
            "password":password,
            "first_name": serializer.validated_data['first_name'],
            "last_name": serializer.validated_data['last_name'],
            "phone_number": serializer.validated_data['phone_number'],
            "role": serializer.validated_data['role'],
            "merchant": request.user.merchant,
            "shop":serializer.validated_data['shop']
        }
        print(request.user.merchant.id)
        # Create the user
        user = User.objects.create_user(**user_data)
        message = (
            f"Hello {user.first_name} {user.last_name},\n\n"
            "Your account has been created successfully on Malawi stores.\n"
            f"You will act as a shop manager for {user.shop.name} shop.\n"
            f"Your Email is: {email} \n"
            f"Your login password is: {password} \n\n"
            "Please log in to https://stores.malipo.mw and change your password immediately.\n"
            "- Malawi Stores Team"
        )
        send_invite_sms.delay('Matikiti', user.phone_number, message)

        response = Response({'message': 'Signup and invite sent successful'})
        return response

class ManagerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            search= request.GET.get('search')
            merchant= request.GET.get('merchant')
            shop= request.GET.get('shop')
            
            if request.user.role == 'super_admin':
                users=User.objects.filter(role='seller')
            elif request.user.role == 'merchant':
                users=User.objects.filter(merchant=request.user.merchant,role='seller')
            elif request.user.role == 'seller':
                users=User.objects.filter(shop=request.user.shop,role='seller')
            else:
                return Response({'message': 'You are not Authorized'}, status=status.HTTP_401_UNAUTHORIZED)
            if search:
                users=users.filter(
                    Q(first_name__icontains=search)|
                    Q(last_name__icontains=search)|
                    Q(phone_number__icontains=search)|
                    Q(merchant__id__icontains=search)|
                    Q(merchant__name__icontains=search)|
                    Q(shop__name__icontains=search)
                )
                
            if merchant:
                users=users.filter(
                    Q(merchant__id__icontains=merchant)
                )
            if shop:
                users=users.filter(
                    Q(shop__slug__icontains=shop)
                )
            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(users, request)
            serializer = UserManagersSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
            # serializer = UserSerializer(users, many=True)
            # return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)