# views.py
from rest_framework import viewsets, permissions
from .models import Region, User
from .serializers import RegionSerializer, UserSerializer
from rest_framework import filters

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_student', 'region']
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['username', 'balance']

    def perform_create(self, serializer):
        # Custom logic if needed before saving a new user
        serializer.save()

    def perform_update(self, serializer):
        # Custom logic if needed before updating a user
        serializer.save()
