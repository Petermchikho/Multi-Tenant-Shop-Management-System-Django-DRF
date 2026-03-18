from django.contrib.auth import authenticate
from custom_user.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from authweb.models import EmailOTP
from authweb.serializers import *
from .serializers import *
from django.core.mail import send_mail
import random
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from authweb.utils import get_id_token_with_code_method_1,get_id_token_with_code_method_2
#authentication_classes = [JWTAuthentication]

# Return the tokens 
def set_tokens(user):
    refresh= RefreshToken.for_user(user)
    
    return {
        'user':UserSerializer(user).data,
        'tokens':{
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }

class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        if User.objects.filter(email=email).exists():
            return Response({'error': 'User already exists'}, status=400)

        otp = str(random.randint(100000, 999999))
        otp_hash = EmailOTP.hash_otp(otp)
        EmailOTP.objects.filter(email=email).delete()
        EmailOTP.objects.create(email=email, otp_hash=otp_hash)
        send_mail('Your OTP', f'Your OTP is {otp}', 'info@mobipay.mw', [email])
        return Response({'message': 'OTP sent'})
    
class SendOTPResetView(APIView):
    def post(self, request):
        serializer =SendOTPResetSerializer(data=request.data)
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

        user = User.objects.create_user(
            email=email,
            password=serializer.validated_data['password'],
            first_name = serializer.validated_data['first_name'],
            last_name = serializer.validated_data['last_name'],
            phone_number=serializer.validated_data['phone_number']
        )
        response = set_tokens(user)
        
        return Response({'data':response,'message': 'Signup successful'})

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class LoginView(APIView):
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        if not user:
            return Response({'error': 'Invalid credentials'}, status=400)
        
        response = set_tokens(user)
        return Response({'data':response,'message': 'Login successful'})



class Login2FAView(APIView):
    def post(self, request):
        # Validate the credentials (email and password)
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Authenticate the user
        user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        
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
        response = set_tokens(user)  # Set tokens as cookies
        
        
        # Optionally, delete the OTP after successful verification for security
        otp_obj.delete()
        
        return Response({'data':response,'message': 'OTP verified. You are now logged in.'})


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token=serializer.validated_data['refresh_token']

        if refresh_token is None:
            return Response({'error': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({'tokens':{
                    'refresh': str(refresh),
                    'access': str(access_token),
                },'message': 'Token refreshed'})
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
            serializer = RefreshTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            refresh_token=serializer.validated_data['refresh_token']
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception as e:
            print("Logout blacklist error:", str(e)) 

        response = Response({'message': 'Logged out'})
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
        user=User.objects.create_user(email=email)
    return user
class LoginWithGoogle(APIView):
    def post(self,request):
        if 'code' in request.data.keys():
            code=request.data['code']
            id_token=get_id_token_with_code_method_2(code)
            user_email=id_token['email']
            user=authenticate_or_create_user(user_email)
            response = Response({'message': 'Login successful'})
            set_tokens(response, user)
            return response
        return Response('ok')
