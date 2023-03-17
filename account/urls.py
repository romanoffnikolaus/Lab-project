from django.urls import path, include
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('profile', views.ProfileView)

urlpatterns = [
    path('register/', views.RegistrationView.as_view(), name="user_registration"),
    path('activate/<str:email>/<str:activation_code>/', views.ActivationView.as_view(), name='activate'),
    path('change-password/', views.ChangePasswordView.as_view(), name="change_password"),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name="forgot_password"),
    path('forgot_password_complete/',views.ForgotPasswordCompleteView.as_view()),
    path('login/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('logout/', views.APILogoutView.as_view(), name='auth_logout'),
    path('', include(router.urls))
]
