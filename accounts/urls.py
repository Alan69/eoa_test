# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, UserViewSet, RegisterView, LoginView, CurrentUserView

router = DefaultRouter()
router.register(r'regions', RegionViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/user/', CurrentUserView.as_view(), name='current-user'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
]
