from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Region
from .forms import UserCreationForm, UserChangeForm
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # form = UserChangeForm
    # add_form = UserCreationForm

    list_display = ('username', 'first_name', 'last_name', 'region', 'school', 'email', 'phone_number', 
                   'referral_percentage', 'referral_status', 'referral_earnings', 'referral_count')
    list_filter = ('is_student', 'is_teacher', 'is_principal', 'is_staff', 'is_active', 'is_superuser', 
                  'region', 'referral_expiry_date')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'region', 'email', 'phone_number', 'school')}),
        ('Balance & Payments', {'fields': ('balance', 'payment_id')}),
        ('Referral System', {
            'fields': (
                'referral_link', 
                'referral_bonus',
                'referral_percentage',
                'referral_expiry_date',
                'referred_by',
                'referral_created_at'
            ),
            'classes': ('wide',)
        }),
        ('Test Information', {'fields': ('test_is_started', 'total_time', 'test_start_time', 'finish_test_time')}),
        ('Permissions', {'fields': ('is_active', 'is_student', 'is_teacher', 'is_principal', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'region', 'school', 'email', 'phone_number', 
                      'password1', 'password2', 'is_student', 'is_teacher', 'is_principal')}
        ),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ('referral_created_at', 'referral_bonus')

    def referral_status(self, obj):
        status = obj.get_referral_status()
        if status == "Active":
            color = "green"
        elif status == "Expired":
            color = "red"
        else:
            color = "grey"
        return format_html('<span style="color: {};">{}</span>', color, status)
    referral_status.short_description = "Referral Status"

    def referral_count(self, obj):
        return obj.referrals.count()
    referral_count.short_description = "Referrals Count"

    def referral_earnings(self, obj):
        return f"{obj.referral_bonus} KZT"
    referral_earnings.short_description = "Total Earnings"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('referrals')
        return queryset

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'region_type', 'description')
    search_fields = ('name',)
    list_filter = ('region_type',)
