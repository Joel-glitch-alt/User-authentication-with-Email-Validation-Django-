# register/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .manager import UserManager
from rest_framework_simplejwt.tokens import RefreshToken


AUTH_PROVIDERS = {'email': 'email', 'google': 'google', 'github': 'github', 'facebook': 'facebook'}

# Custom User Model
class User(AbstractUser, PermissionsMixin):
    username = None  #  remove username completely
    email = models.EmailField(max_length=255, unique=True, verbose_name=_("email address"))
    first_name = models.CharField(max_length=255, verbose_name=_("first name"))
    last_name = models.CharField(max_length=255, verbose_name=_("last name"))
    is_staff = models.BooleanField(default=False, verbose_name=_("staff status"))
    is_superuser = models.BooleanField(default=False, verbose_name=_("superuser status"))
    is_verified = models.BooleanField(default=False, verbose_name=_("verified status"))
    is_active = models.BooleanField(default=True, verbose_name=_("active status"))
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_("date joined"))
    last_login = models.DateTimeField(auto_now=True, verbose_name=_("last login"))
    auth_provider = models.CharField(max_length=50, default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email
    
    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


# OTP Model
class OneTimePassword(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,   # ✅ proper way to reference custom user
        on_delete=models.CASCADE,
        related_name="otp"
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.code}"
