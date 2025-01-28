from datetime import timezone
from django.conf import settings

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.contenttypes.fields import GenericRelation
# Şirket Modeli
class Company(models.Model):
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    contract_start_date = models.DateField(blank=True, null=True)
    contract_end_date = models.DateField(blank=True, null=True)
    create_user = models.ForeignKey('LdapUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_companies')  # Unique related_name
    code = models.CharField(max_length=20, unique=True)
    is_founder = models.BooleanField(default=False)

    def __str__(self):
        return self.name
# LDAP Bağlantı Parametreleri
from cryptography.fernet import Fernet
from django.conf import settings
import base64
from django.contrib.auth.hashers import make_password, check_password
class LdapConfig(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,related_name='ldap_configs')
    ldap_server = models.CharField(max_length=255)
    ldap_port = models.IntegerField(default=389,null=True,blank=True)  # LDAP portu (389 varsayılan)
    base_dn = models.CharField(max_length=255)
    bind_username = models.CharField(max_length=255)
    bind_dn = models.CharField(max_length=255)
    bind_password = models.TextField()  # Şifre şifrelenmiş olarak saklanacak

    def save(self, *args, **kwargs):
        cipher_suite = Fernet(settings.SECRET_KEY.encode())  # Fernet objesi oluştur
        self.bind_password = cipher_suite.encrypt(self.bind_password.encode()).decode()
        super().save(*args, **kwargs)

    def get_decrypted_password(self):
        cipher_suite = Fernet(settings.SECRET_KEY.encode())
        return cipher_suite.decrypt(self.bind_password.encode()).decode()
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager


    # Kullanıcı İzinleri
from django.contrib.auth import get_user_model
# class UserMail(models.Model):
#     user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_mails')  # Her kullanıcı için bir e-posta hesabı
#     subject = models.CharField(max_length=255)
#     sender = models.EmailField()
#     received_at = models.DateTimeField(auto_now_add=True)
#     body = models.TextField()
#     company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='emails')
#     relating = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='emails')

#     def __str__(self):
#         return f"{self.subject} - {self.user.email_address}"
# class Permission(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE)
#     user = models.ForeignKey(LdapUser, on_delete=models.CASCADE)
#     add_company = models.BooleanField(default=False)
#     add_user = models.BooleanField(default=False)
    
#     def __str__(self):
#         return f"Permissions for {self.user.user.username} in {self.company.name}"

class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
class Category(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False, blank=False)
    created_by_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    created_by_object_id = models.PositiveIntegerField(null=True, blank=True)
    created_by = GenericForeignKey('created_by_content_type', 'created_by_object_id')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name if self.is_active else f"{self.name} (Inactive)"

    class Meta:
        db_table = "Category"

class Brand(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Yeni ekleme
    name = models.CharField(max_length=50, null=False, blank=False)
    created_by_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    created_by_object_id = models.PositiveIntegerField(null=True, blank=True)
    created_by = GenericForeignKey('created_by_content_type', 'created_by_object_id')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Brand"

class Model(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=50, null=False, blank=False)
    created_by_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_by_models'
    )
    created_by_object_id = models.PositiveIntegerField(null=True, blank=True)
    created_by = GenericForeignKey('created_by_content_type', 'created_by_object_id')
    is_active = models.BooleanField(default=True)
    unit = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Model"

class ProductStatus(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False, blank=False)
    created_by_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    created_by_object_id = models.PositiveIntegerField(null=True, blank=True)
    created_by = GenericForeignKey('created_by_content_type', 'created_by_object_id')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "ProductStatus"
from django.contrib.contenttypes.fields import GenericRelation
class Product(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    model = models.ForeignKey(Model, on_delete=models.SET_NULL, null=True, blank=True)
    created_by_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_by_products'
    )
    created_by_object_id = models.PositiveIntegerField(null=True, blank=True)
    created_by = GenericForeignKey('created_by_content_type', 'created_by_object_id')
    is_active = models.BooleanField(default=True)
    serial_number = models.CharField(max_length=255, null=False, blank=False)
    status = models.ForeignKey(ProductStatus, on_delete=models.SET_NULL, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Generic Foreign Key for assign_to (Product'a atanan kullanıcı)
    assign_to_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assign_to_products'
    )
    assign_to_object_id = models.PositiveIntegerField(null=True, blank=True)
    assign_to = GenericForeignKey('assign_to_content_type', 'assign_to_object_id')

    # Generic Foreign Key for assign_by (Ürünü atayan kullanıcı)
    assign_by_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assign_by_products'
    )
    assign_by_object_id = models.PositiveIntegerField(null=True, blank=True)
    assign_by = GenericForeignKey('assign_by_content_type', 'assign_by_object_id')

    class Meta:
        db_table = 'Product'

    def __str__(self):
        return f"{self.category} - {self.brand} - {self.model}"
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email gereklidir')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    # İstediğiniz alanları buraya ekleyebilirsiniz
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True, related_name='custom_users')  # related_name ekledik
    company_code = models.CharField()  # Şirket kodu
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    objects = CustomUserManager()  # CustomUserManager kullanıldığından emin olun
    tag = models.CharField(max_length=50)
    assigned_products = GenericRelation(Product, related_query_name='assigned_to')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    def __str__(self):
        return self.username
    @classmethod
    def get_by_natural_key(cls, username):
        return cls.objects.get(username=username)

class LdapUser(AbstractBaseUser):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True, related_name='ldap_users')  
    company_code = models.CharField(max_length=255)  # Şirket kodu
    username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    email_password = models.CharField(max_length=255)
    ldap_dn = models.CharField(max_length=1024, unique=False)
    is_founder = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()
    assigned_products = GenericRelation(Product, related_query_name='assigned_to')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='ldapuser_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='ldapuser_permissions',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        unique_together = ('company_code', 'username')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
class LdapGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Grup ismi
    description = models.TextField(null=True, blank=True)  # Grup açıklaması (isteğe bağlı)
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='ldap_groups',
        null=True,  # Null değerine izin ver
        blank=True,
    )  # Şirketle ilişkilendirme
    users = models.ManyToManyField(
        LdapUser, 
        related_name='ldap_groups',
        blank=True
    )  # Kullanıcılar ile Many-to-Many ilişki

    created_at = models.DateTimeField(auto_now_add=True)  # Oluşturulma zamanı
    updated_at = models.DateTimeField(auto_now=True)  # Güncellenme zamanı

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class AssetAssignment(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE)  # Ürün ile ilişki
    appointed_company = models.CharField(max_length=255, null=True, blank=True)
    appointed_address = models.CharField(max_length=255, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Ürün ile ilişki

    # Kullanıcıların GenericForeignKey ile atanması
    assign_by_content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, null=False, blank=False, related_name="assign_by")
    assign_by_object_id = models.PositiveIntegerField(null=False, blank=False)
    assign_by = GenericForeignKey('assign_by_content_type', 'assign_by_object_id')  # Atayan kişi

    assign_to_content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, null=False, blank=False, related_name="assign_to")
    assign_to_object_id = models.PositiveIntegerField(null=False, blank=False)
    assign_to = GenericForeignKey('assign_to_content_type', 'assign_to_object_id')  # Atanan kişi

    info = models.TextField(blank=True, null=True)  # Ekstra bilgi
    assign_date = models.DateTimeField(auto_now_add=True)  # Atama tarihi
    assign_status = models.CharField(max_length=50, default='active')  # Atama durumu (ör. 'active', 'inactive', 'returned' vb.)
    created_at = models.DateTimeField(auto_now_add=True)  # Kayıt oluşturulma tarihi
    updated_at = models.DateTimeField(auto_now=True)  # Kayıt güncellenme tarihi
    is_active = models.BooleanField(default=True)  # Aktiflik durumu
    return_date = models.DateTimeField(null=True, blank=True)  # Geri iade tarihi (isteğe bağlı)
    return_status = models.CharField(max_length=50, null=True, blank=True)  # Geri iade durumu (isteğe bağlı)
    return_user_content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="return_user")
    return_user_object_id = models.PositiveIntegerField(null=True, blank=True)
    return_user = GenericForeignKey('return_user_content_type', 'return_user_object_id')  # Atanan kişi
    batch_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.product} assigned to"
    
class ABC(models.Model):
    name = models.CharField()