from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

# app-name="userauth"

class User(AbstractUser):
    email=models.EmailField(unique=True)
    # phoneno=models.PhoneNumberField(max_length=20, unique=True)
    phoneno=PhoneNumberField()
    username=models.CharField(max_length=100,unique=True)

    USERNAME_FIELD="email"
    REQUIRED_FIELDS=['username','phoneno']

    def __str__(self):
        return self.username
    
# class EmailVerification(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     otp = models.IntegerField()
#     is_verified = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.user.username} - {self.otp}"
    
    



# Create your models here.
