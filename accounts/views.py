# views.py
from rest_framework import viewsets, permissions
from .models import Region, User
from .serializers import RegionSerializer, UserSerializer
from rest_framework import filters
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from django.contrib.auth import get_user_model
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

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

class CurrentUserView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        # refresh = RefreshToken.for_user(user)
        return Response({
            # 'refresh': str(refresh),
            # 'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })