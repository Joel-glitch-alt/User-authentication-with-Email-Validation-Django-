from django.urls import path
from .views import RegisterUserView, VerifyUserEmail,LoginView,TestAuthenticatedView,PasswordResetConfirm,PasswordResetRequestView,SetNewPassword,LogoutView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify'),
    path('login/', LoginView.as_view(), name='login'),
    path('test-auth/', TestAuthenticatedView.as_view(), name='test-auth'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetNewPassword.as_view(), name='set-new-password'), 
    path('logout/', LogoutView.as_view(), name='logout'),
]
