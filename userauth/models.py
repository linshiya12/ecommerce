from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from user.models import *

# app-name="userauth"

class User(AbstractUser):
    email=models.EmailField(unique=True)
    # phoneno=models.PhoneNumberField(max_length=20, unique=True)
    phoneno=PhoneNumberField()
    username=models.CharField(max_length=100,unique=True)
    referral_code = models.CharField(max_length=100, unique=True, null=True)
    

    USERNAME_FIELD="email"
    REQUIRED_FIELDS=['username','phoneno']

    def __str__(self):
        return self.username
    
    



# Create your models here.
