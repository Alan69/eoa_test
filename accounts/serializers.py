from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import Region
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all(), required=False, allow_null=True)
    referral_code = serializers.CharField(required=False, write_only=True, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password2', 'region', 'school', 'phone_number', 'referral_code')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # Handle referral code validation
        referral_code = attrs.get('referral_code', None)
        print(f"Raw referral code received: {referral_code}")
        
        if referral_code:
            try:
                # Find user by referral code directly
                referrer = User.objects.filter(
                    referral_link__contains=referral_code,
                    referral_expiry_date__gt=datetime.now()
                ).first()
                
                if referrer:
                    print(f"Found referrer: {referrer.username}")
                    attrs['referred_by'] = referrer
                else:
                    print("No active referrer found with this code")
                    raise serializers.ValidationError({"referral_code": "Invalid or expired referral link"})
            except Exception as e:
                print(f"Error processing referral: {str(e)}")
                raise serializers.ValidationError({"referral_code": f"Invalid referral link: {str(e)}"})
        
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2', None)
        referrer = validated_data.pop('referred_by', None)
        
        print(f"Creating user with data: {validated_data}")
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        if referrer:
            print(f"Setting referrer for user {user.username} to {referrer.username}")
            user.referred_by = referrer
            user.save()
            print(f"User {user.username} successfully linked to referrer {referrer.username}")
            
            # Add this user to referrer's referrals
            referrer.referrals.add(user)
            referrer.save()
            print(f"Added user {user.username} to referrer's {referrer.username} referrals")
        
        return user

class UserSerializer(serializers.ModelSerializer):

    region = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'region', 'school', 'phone_number', 'balance', 'referral_link', 'referral_bonus', 'test_is_started')

    def get_region(self, obj):
        return obj.region.name if obj.region else None

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    new_password2 = serializers.CharField(write_only=True, required=True)

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'region_type', 'description']

class UserPUTSerializer(serializers.ModelSerializer):
    # region = RegionSerializer()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'region', 'school', 'referral_link', 'referral_bonus']
        # read_only_fields = ['email']  # Email should not be updated in your form.
