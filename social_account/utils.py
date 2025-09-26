from google.auth.transport import requests
from google.oauth2 import id_token
from account.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed



# Google OAuth2
class Google():
    @staticmethod
    def validate(access_token):
        try:
            id_info = id_token.verify_oauth2_token(access_token, requests.Request())
            if "account.google.com" in id_info['iss']:
                return id_info
        except Exception as e:
            return "token is invalid or has expired!"
        


def register_social_user(provider, email, first_name, last_name):
    user = User.objects.filter(email=email)
    if user.exists():
        if provider == user[0].auth_provider:
            login_user = authenticate(email=email, password=settings.SOCIAL_AUTH_PASSWORD)
            user_tokens = login_user.tokens()
            return {
            "email": user.email,
            "full_name": login_user.full_name,
            "access_token":str(user_tokens["access"]),
            "refresh_token": str(user_tokens["refresh"]),
        }

        else:
            raise AuthenticationFailed(
                detail=f'Please continue your login using {user[0].auth_provider}'
            )
        
    new_user ={
         'email': email,
         'first_name': first_name,
         'last_name': last_name,
         'password': settings.SOCIAL_AUTH_PASSWORD
        }
    register_user =User = User.objects.create_user(**new_user)
    register_user.auth_provider = provider
    register_user.is_verified = True
    register_user.save()
    login_user = authenticate(email=email, password=settings.SOCIAL_AUTH_PASSWORD)
    user_tokens = login_user.tokens()
    return {
            "email": user.email,
            "full_name": login_user.full_name,
            "access_token":str(user_tokens["access"]),
            "refresh_token": str(user_tokens["refresh"]),
        }
    #user = authenticate(email=email, password=settings.SOCIAL_AUTH_PASSWORD)