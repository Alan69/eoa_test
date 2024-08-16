from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, CustomTokenObtainPairView, UserDetailView, LogoutView, signup, login

urlpatterns = [
    path('api/register/', signup, name='register'),
    path('api/login/', login, name='token_obtain_pair'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/', UserDetailView.as_view(), name='user_detail'),
]
