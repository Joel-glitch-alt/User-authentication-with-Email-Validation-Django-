from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import UserRegisterSerializer,LoginSerializer,PasswordResetRequestSerializer
from .utils import send_otp_via_email
from .models import OneTimePassword, user
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            send_otp_via_email(user['email'])  # ✅ send OTP to email

            return Response({
                "data": user,
                "message": f"hi {user['first_name']}, your account was created successfully"
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Verify Email View 
class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        otpcode=request.data.get('otp')
        try:
            user_code_obj=OneTimePassword.objects.get(code=otpcode)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    'message' : 'OTP verified successfully'
                }, status = status.HTTP_200_OK)
            return Response({
                'message': 'OTP already verified'
            }, status = status.HTTP_204_NO_CONTENT)
        
        except OneTimePassword.DoesNotExist:
            return Response({
                'message': 'Invalid OTP code'
            }, status=status.HTTP_400_BAD_REQUEST)



#Login View
class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context = {'request': request})
        serializer.is_valid(raise_exception = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# A protected view to test authentication
class TestAuthenticatedView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {
            "message": "You are authenticated"
        }

        return Response(data, status=status.HTTP_200_OK)
    
#Password Reset View (Optional)
class PasswordResetRequestView(GenericAPIView):
    
     serializer_class = PasswordResetRequestSerializer
     def post(self, request):
         serializer = self.serializer_class(data=request.data, context = { 'request': request})
         serializer.is_valid(raise_exception = True)
         return Response({
            'message': 'We have sent you a link to reset your password, please check your email'
         }, status = status.HTTP_200_OK 
         )


# Password Reset Confirm View (Optional)
class PasswordResetConfirm(GenericAPIView):
     def get(self, request, uidb64, token):
          try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user= user.objects.get(id = user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({
                    'message': 'Token is not valid, please request a new one'
                }, status = status.HTTP_401_UNAUTHORIZED)
                return Response({
                    'success':True, 'message': 'Token is valid, you can now reset your password', 'uidb64': uidb64, 'token': token
                }, status = status.HTTP_200_OK)

         except DjangoUnicodeDecodeError:
                return Response({
                    'message': 'Token is not valid, please request a new one'
                }, status = status.HTTP_401_UNAUTHORIZED
                )

class SetNewPassword(GenericAPIView):
        def patch(self, request):
