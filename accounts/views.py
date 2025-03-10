from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Region
from django.contrib.auth.hashers import check_password
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer, UserPUTSerializer, RegionSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

# Customizing TokenObtainPairSerializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token

# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     permission_classes = (permissions.AllowAny,)
#     serializer_class = RegisterSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        print("Login attempt with username:", request.data.get('username'))
        try:
            user = User.objects.get(username=request.data.get('username'))
            print(f"Found user: {user.username}")
            print(f"User active status: {user.is_active}")
            print(f"Password valid: {user.check_password(request.data.get('password'))}")
        except User.DoesNotExist:
            print("User not found")
        
        return super().post(request, *args, **kwargs)

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_200_OK)

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response("missing user", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
        operation_description="Возвращяет auth юзера",
        responses={201: openapi.Response('success')}
    )
def current_user_view(request):
    user = request.user
    user_data = UserSerializer(user).data
    
    return Response({"user_data": user_data})

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_description="Register a new user",
        responses={201: openapi.Response('User registered successfully')}
    )

    def post(self, request, *args, **kwargs):
        print("Registration request data:", request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        print(f"User created: {user.username}")
        print(f"User active status: {user.is_active}")
        print(f"User password set: {user.has_usable_password()}")

        # Ensure user is active
        if not user.is_active:
            user.is_active = True
            user.save()
            print("User activated")

        # Generate a token for the new user
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password changed successfully.",
                examples={
                    "application/json": {
                        "new_password": "new_password_value",
                        "refresh": "new_refresh_token",
                        "access": "new_access_token",
                    }
                }
            ),
            400: "Bad Request - Passwords don't match or invalid current password.",
        }
    )
    def post(self, request):
        user = request.user
        data = request.data

        # Get the required fields from request data
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        new_password2 = data.get('new_password2')

        # Check if all fields are provided
        if not all([current_password, new_password, new_password2]):
            return Response({"detail": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the current password matches the user's actual password
        if not check_password(current_password, user.password):
            return Response({"detail": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if new password matches the confirmation
        if new_password != new_password2:
            return Response({"detail": "New passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password and save the user
        user.set_password(new_password)
        user.save()

        # Generate new refresh token
        refresh = RefreshToken.for_user(user)

        return Response({
            "new_password": new_password,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='put',
    request_body=UserPUTSerializer,  # Define the input serializer
    responses={  # Define the possible response codes and serializers
        200: UserPUTSerializer,  # Successful response with updated user data
        400: openapi.Response('Invalid input'),  # Bad request response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])  # Ensure only authenticated users can update their profile
def update_user_view(request):
    user = request.user  # Get the current user making the request
    
    # Deserialize the incoming data and validate it
    serializer = UserPUTSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()  # Update the user's data
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    operation_description="Generate or retrieve a referral link for the current user",
    responses={
        200: openapi.Response(
            description="Referral link generated/retrieved successfully",
            examples={
                "application/json": {
                    "referral_link": "example-referral-code",
                    "referral_bonus": "1500.00"
                }
            }
        )
    }
)
def generate_referral_link(request):
    user = request.user
    referral_link = user.generate_referral_link()
    
    return Response({
        "referral_link": referral_link,
        "referral_bonus": user.referral_bonus
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    operation_description="Get list of users who signed up using current user's referral link",
    responses={
        200: openapi.Response(
            description="List of referred users retrieved successfully",
            examples={
                "application/json": {
                    "referrals": [
                        {
                            "username": "user123",
                            "first_name": "John",
                            "last_name": "Doe",
                            "joined_at": "2024-03-20T12:00:00Z",
                            "total_purchases": "1500.00"
                        }
                    ]
                }
            }
        )
    }
)
def get_referred_users(request):
    user = request.user
    # print(f"Getting referrals for user: {user.username}")
    
    referred_users = user.referrals.all().order_by('-id')
    # print(f"Found {referred_users.count()} referrals")
    
    referral_data = []
    for referred_user in referred_users:
        # print(f"Processing referral: {referred_user.username}")
        data = {
            "username": referred_user.username,
            "first_name": referred_user.first_name,
            "last_name": referred_user.last_name,
            "total_purchases": str(referred_user.total_purchases or '0.00')
        }
        referral_data.append(data)
        # print(f"Added referral data: {data}")
    
    # print(f"Final referral data: {referral_data}")
    return Response(referral_data)