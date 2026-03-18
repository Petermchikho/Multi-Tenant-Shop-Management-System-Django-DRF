from django.urls import path
from .views import *

urlpatterns = [
    path('auth/send-otp/', SendOTPView.as_view()),
    path('auth/send-otp/password', SendOTPResetView.as_view()),
    path('auth/2FA/login',Login2FAView.as_view()),
    path('auth/2FA/verify-otp/', VerifyOTP2FAView.as_view()),
    path('auth/signup/', SignupView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('auth/me/', MeView.as_view()),
    path('auth/change-password/', ChangePasswordView.as_view()),
    path('auth/reset-password/', ResetPasswordView.as_view()),
    path('auth/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/google',LoginWithGoogle.as_view(),name='login-with-google'),
]
