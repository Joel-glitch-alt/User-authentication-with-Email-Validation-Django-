from rest_framework import serializers
from .models import User  
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import send_normal_email


# Serializer for User Registration
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
        validated_data.pop('password2')  # remove password2
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],  # automatically hashed
        )
        return user
    
    # Serializer for User Login
class LoginSerializer(serializers.ModelSerializer):
        email = serializers.EmailField(max_length = 225, min_length = 6)
        password = serializers.CharField(max_length =68, write_only = True)
        full_name = serializers.CharField(max_length = 100, read_only = True)
        access_token = serializers.CharField(max_length = 255, read_only = True)
        refresh_token = serializers.CharField(max_length = 255, read_only = True)

        class Meta:
             model = User
             fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token']

        def validate(self, attrs):
             email = attrs.get('email')
             password = attrs.get('password')
             request = self.context.get('request')
             user = authenticate(request, email=email, password=password)
             if not user:
                  raise AuthenticationFailed('Invalid credentials, try again')
             if not user.is_verified:
                  raise AuthenticationFailed('Email is not verified')
             user_tokens  = user.tokens()

             # return user details and tokens
             return {
                  'email': user.email,
                  'full_name': user.get_full_name,
                  'access_token': str(user_tokens.get('access')),
                  'refresh_token': str(user_tokens.get('refresh'))
             }
        
# Password Reset Request Serializer
class PasswordResetRequestSerializer(serializers.Serializer):
     email = serializers.EmailField(max_length =255)


     class Meta:
            fields = ['email']

     def validate_email(self, attrs):
          email = attrs.get('email')
          if User.objects.filter(email = email).exists():
               user = User.objects.get(email = email)
               uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
               token = PasswordResetTokenGenerator().make_token(user)
               request = self.context.get('request')
               site_domain = get_current_site(request).domain
               relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
               abslink = "http://{site_domain}{relative_link}"
               email_body = f'Hello, \n Use the link below to reset your password \n {abslink}'
               data = {
                    'email_body': email_body,
                    'to_email': user.email,
                    'email_subject': 'Reset your password'
               }
               send_normal_email(data)


          return super().validate(attrs) 