# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, UserViewSet

router = DefaultRouter()
router.register(r'regions', RegionViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
