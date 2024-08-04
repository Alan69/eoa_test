# serializers.py
from rest_framework import serializers
from .models import Region, User

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'region_type', 'description']
        read_only_fields = ['id']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'region',
            'school', 'phone_number', 'balance', 'referral_link', 'referral_bonus',
            'payment_id', 'is_student', 'is_teacher', 'is_principal',
            'is_staff', 'is_active', 'is_superuser'
        ]
        read_only_fields = ['id', 'balance', 'referral_link', 'referral_bonus']
