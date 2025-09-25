from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    UserRegisterSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    SetNewPasswordSerializer
)
from .utils import send_otp_via_email
from .models import OneTimePassword
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model

# ✅ Always use get_user_model() to reference the custom User model
User = get_user_model()


# ✅ Register User
class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            send_otp_via_email(user['email'])  # Send OTP to email

            return Response({
                "data": user,
                "message": f"Hi {user['first_name']}, your account was created successfully"
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Verify Email OTP
class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        otpcode = request.data.get('otp')
        try:
            user_code_obj = OneTimePassword.objects.get(code=otpcode)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    'message': 'OTP verified successfully'
                }, status=status.HTTP_200_OK)
            return Response({
                'message': 'OTP already verified'
            }, status=status.HTTP_200_OK)

        except OneTimePassword.DoesNotExist:
            return Response({
                'message': 'Invalid OTP code'
            }, status=status.HTTP_400_BAD_REQUEST)


# ✅ Login View
# class LoginUserView(GenericAPIView):
#     serializer_class = LoginSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)



# ✅ Protected Test View
class TestAuthenticatedView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {"message": "You are authenticated"}
        return Response(data, status=status.HTTP_200_OK)


# ✅ Password Reset Request
class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({
            'message': 'We have sent you a link to reset your password, please check your email'
        }, status=status.HTTP_200_OK)


# ✅ Password Reset Confirm
class PasswordResetConfirm(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user_obj = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user_obj, token):
                return Response({
                    'message': 'Token is not valid, please request a new one'
                }, status=status.HTTP_401_UNAUTHORIZED)

            return Response({
                'success': True,
                'message': 'Token is valid, you can now reset your password',
                'uidb64': uidb64,
                'token': token
            }, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            return Response({
                'message': 'Token is not valid, please request a new one'
            }, status=status.HTTP_401_UNAUTHORIZED)


# ✅ Set New Password
class SetNewPassword(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            'message': 'Password reset successful'
        }, status=status.HTTP_200_OK)
