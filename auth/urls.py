from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('register.urls')),  # this exposes /register/
    path('api/v1/auth/', include('socail_account.urls')),  # this exposes /api/v1/auth/
]
