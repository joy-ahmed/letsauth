from django.db import models 
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number must be set")
        user = self.model(phone_number = phone_number, **extra_fields)
        user.set_password(password)
        user.generate_verification_token()
        user.email_verification()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_superuser(phone_number, password, **extra_fields)

    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True) 
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    verification_token = models.CharField(max_length=100, blank=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'phone_number'

    class Meta:
        db_table = 'custom_user'
    

    def __str__(self):
        return self.phone_number
    
    def get_full_name(self):
        full_name = '%s %s %s'  % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name
    
    def generate_verification_token(self):
        self.verification_token = get_random_string(50)

    def email_verification(self):
        subject = 'Account Verification'
        message = f'Hi {self.first_name}, \n\nThank you for registering. Please click the following link to verify your account\n\nhttp://127.0.0.1:8000/verify/?token={self.verification_token}'
        send_mail(subject, message, 'joy572064@gmail.com', [self.email])
