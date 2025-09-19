from django.urls import path
from .views import RegisterUserView, VerifyUserEmail,LoginUserView,TestAuthenticatedView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('test-auth/', TestAuthenticatedView.as_view(), name='test-auth'),
]
