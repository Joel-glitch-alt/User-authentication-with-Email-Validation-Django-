from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import send_normal_email
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


# ✅ User Registration
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
        )


# ✅ User Login

# class LoginSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(max_length=225, min_length=6)
#     password = serializers.CharField(max_length=68, write_only=True)
#     full_name = serializers.CharField(max_length=100, read_only=True)
#     access_token = serializers.CharField(max_length=255, read_only=True)
#     refresh_token = serializers.CharField(max_length=255, read_only=True)

#     class Meta:
#         model = User
#         fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token']

#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')
#         request = self.context.get('request')
#         user = authenticate(request, email=email, password=password)

#         if not user:
#             raise AuthenticationFailed('Invalid credentials, try again')
#         if not user.is_verified:
#             raise AuthenticationFailed('Email is not verified')

#         user_tokens = user.tokens()
#         return {
#             'email': user.email,
#             'full_name': user.get_full_name(),
#             'access_token': str(user_tokens.get('access')),
#             'refresh_token': str(user_tokens.get('refresh')),
#         }
    
    ############################################################


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(read_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        request = self.context.get("request")

        # ✅ Authenticate using email (USERNAME_FIELD = 'email')
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid email or password.")
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified.")

        # ✅ Use property (NO parentheses!)
        full_name = user.get_full_name

        # ✅ Use the tokens() helper you defined in the model
        tokens = user.tokens()

        return {
            "email": user.email,
            "full_name": full_name,
            "access_token": tokens["access"],
            "refresh_token": tokens["refresh"],
        }




# ✅ Password Reset Request
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate_email(self, value):
        """
        DRF passes the email string as `value`.
        """
        email = value.lower()
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get('request')
            site_domain = get_current_site(request).domain
            relative_link = reverse(
                'password-reset-confirm',
                kwargs={'uidb64': uidb64, 'token': token}
            )
            abslink = f"http://{site_domain}{relative_link}"
            email_body = f'Hello,\nUse the link below to reset your password:\n{abslink}'
            data = {
                'email_body': email_body,
                'to_email': user.email,
                'email_subject': 'Reset your password'
            }
            send_normal_email(data)
        # Always return the value
        return email


# ✅ Set New Password
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    confirm_password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    uidb64 = serializers.CharField(max_length=255, write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('The reset link is invalid')

            if password != confirm_password:
                raise serializers.ValidationError('Passwords do not match')

            user.set_password(password)
            user.save()
            return user
        except DjangoUnicodeDecodeError:
            raise AuthenticationFailed('The reset link is invalid or expired')
        

# ✅ Logout Serializer (Optional)
class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    default_error_messages = {
        'bad_token': ('Token is expired or invalid')
    }


    def validate(self, attrs):
        self.token=attrs.get('refresh_token')
        return attrs
    
    def save(self, **kwargs):
        try:
           token =  RefreshToken(self.token)
           token.blacklist()
        except TokenError:
            return self.fail('bad_token')
