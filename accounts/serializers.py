from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import Region

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
        referral_code = attrs.pop('referral_code', None)
        print(f"Validating referral code: {referral_code}")
        if referral_code:
            try:
                referrer = User.objects.get(referral_link=referral_code)
                print(f"Found referrer: {referrer.username}")
                attrs['referred_by'] = referrer
            except User.DoesNotExist:
                print(f"No user found with referral code: {referral_code}")
                raise serializers.ValidationError({"referral_code": "Invalid referral code"})
        else:
            print("No referral code provided")

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2', None)
        referrer = validated_data.pop('referred_by', None)
        
        print(f"Creating user with data: {validated_data}")
        # Create the user with other fields
        user = User.objects.create_user(
            password=password,  # Pass password to create_user
            **validated_data  # This will include username and all other fields
        )
        
        # Handle referral
        if referrer:
            print(f"Applying referral from user {referrer.username}")
            user.referred_by = referrer
            user.save()
            # Apply bonus to referrer
            print(f"Referrer's current balance: {referrer.balance}")
            print(f"Referrer's current bonus: {referrer.referral_bonus}")
            referrer.apply_referral_bonus()
            print(f"Referrer's new balance: {referrer.balance}")
            print(f"Referrer's new bonus: {referrer.referral_bonus}")
        else:
            print("No referrer found in validated data")

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
