from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from .business import Business
from django.contrib.sessions.models import Session

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class RoleChoices(models.TextChoices):
        BUSINESS = 'manager', 'Manager'
        CUSTOMER = 'customer', 'Customer'
        COLLABORATOR = 'collaborator', 'Collaborator'

    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=50, choices=RoleChoices.choices, default=RoleChoices.CUSTOMER)
    businesses = models.ManyToManyField(Business, through='UserBusiness', related_name='users', blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_session_key = models.CharField(max_length=40, null=True, blank=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']
    
    def clear_session(self):
        """Déconnecte l'utilisateur en supprimant la session actuelle."""
        if self.current_session_key and Session.objects.filter(pk=self.current_session_key).exists():
            Session.objects.get(pk=self.current_session_key).delete()
            self.current_session_key = None
            self.save()
    def __str__(self):
        return f"{self.email} | {self.role}"

    def is_business(self):
        return self.role == self.RoleChoices.BUSINESS

    def is_customer(self):
        return self.role == self.RoleChoices.CUSTOMER
    
class UserBusiness(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'business'] 