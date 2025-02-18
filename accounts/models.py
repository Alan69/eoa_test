from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid
from decimal import Decimal
from django.utils import timezone

class Region(models.Model):
    CITY = 'Город'
    VILLAGE = 'Село'

    REGION_TYPE_CHOICES = [
        (CITY, 'Город'),
        (VILLAGE, 'Село'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="Название региона")
    region_type = models.CharField(max_length=10, choices=REGION_TYPE_CHOICES, default=CITY, verbose_name="Тип региона")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_region_type_display()})"

class CustomUserManager(BaseUserManager):
    def _create_user(self, username, password, first_name, last_name, **extra_fields):
        if not username:
            raise ValueError("Необходимо указать логин")
        if not password:
            raise ValueError("Необходимо ввести пароль")

        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('Users must have a username')
        if not email:
            raise ValueError('Users must have an email address')

        # Remove referral_code from extra_fields since it's not a model field
        referral_code = extra_fields.pop('referral_code', None)
        
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, password, first_name, last_name, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(db_index=True, unique=True, max_length=254, verbose_name="ИИН")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    first_name = models.CharField(max_length=250, verbose_name="Имя")
    last_name = models.CharField(max_length=250, verbose_name="Фамилия")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Город")
    school = models.CharField(max_length=255, verbose_name="Образовательное учреждение", null=True, blank=True)
    phone_number = models.CharField(max_length=15, verbose_name="Номер телефона", null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Баланс")
    
    # Referral fields
    referral_link = models.URLField(max_length=255, unique=True, null=True, blank=True, verbose_name="Реферальная ссылка")
    referral_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Бонус с рефералов")
    referral_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, verbose_name="Процент реферала")
    referral_expiry_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата истечения реферала")
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals',
        verbose_name="Реферал от"
    )
    referral_created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания реферала")
    
    payment_id = models.CharField(max_length=255, null=True, blank=True)

    test_is_started = models.BooleanField(default=False)
    total_time = models.IntegerField(default=0)
    test_start_time = models.DateTimeField(null=True, blank=True)
    finish_test_time = models.DateTimeField(null=True, blank=True)

    product = models.ForeignKey('test_logic.Product', on_delete=models.SET_NULL, null=True, blank=True)
    # class_name = models.CharField(max_length=255, verbose_name="Класс", null=True, blank=True)

    is_student = models.BooleanField(default=False, verbose_name="Это студент?")
    is_teacher = models.BooleanField(default=False, verbose_name="Это учитель?")
    is_principal = models.BooleanField(default=False, verbose_name="Это директор?")
    is_staff = models.BooleanField(default=False, verbose_name="Это сотрудник?")
    is_active = models.BooleanField(default=True, verbose_name="Активность?")
    is_superuser = models.BooleanField(default=False, verbose_name="Суперадмин")

    total_purchases = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Сумма покупок")

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    def transfer_balance(self, recipient, amount):
        if self.balance < amount:
            raise ValueError("Insufficient balance to transfer.")
        if not recipient.is_student:
            raise ValueError("Recipient must be a student.")
        
        self.balance -= amount
        recipient.balance += amount
        self.save()
        recipient.save()
    
    def generate_referral_link(self):
        """Generate a referral link for the user"""
        if not self.referral_link:
            import hashlib
            from datetime import timedelta
            
            # Create a unique string using timezone-aware datetime
            unique_string = f"{self.username}-{timezone.now().timestamp()}"
            hash_object = hashlib.sha256(unique_string.encode())
            ref_code = hash_object.hexdigest()[:8]
            
            # Create the full referral link with frontend URL
            base_url = "https://synaqtest.kz"
            self.referral_link = f"{base_url}/signup?ref={ref_code}"
            
            # Set expiry date using timezone-aware datetime
            self.referral_expiry_date = timezone.now() + timedelta(days=365)
            self.save()
        
        return self.referral_link

    def apply_referral_bonus(self, purchase_amount):
        """Apply the referral bonus when a referred user makes a purchase"""
        if self.referral_expiry_date and timezone.now() > self.referral_expiry_date:
            print(f"Referral expired for user {self.username}")
            return False
            
        # Calculate bonus amount based on percentage
        bonus_amount = (Decimal(purchase_amount) * Decimal(self.referral_percentage)) / Decimal(100)
        print(f"Calculating bonus for user {self.username}")
        print(f"Purchase amount: {purchase_amount}")
        print(f"Referral percentage: {self.referral_percentage}%")
        print(f"Bonus amount: {bonus_amount}")
        
        # Add bonus to user's balance and total referral bonus
        self.balance += bonus_amount
        self.referral_bonus += bonus_amount
        self.save()
        
        print(f"Applied bonus of {bonus_amount} KZT to user {self.username}")
        print(f"New balance: {self.balance} KZT")
        print(f"Total referral bonus: {self.referral_bonus} KZT")
        return True

    def get_referral_status(self):
        """Get the status of the referral link"""
        if not self.referral_expiry_date:
            return "Inactive"
        
        if timezone.now() > self.referral_expiry_date:
            return "Expired"
        
        return "Active"