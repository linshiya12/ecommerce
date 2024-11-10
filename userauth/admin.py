from django.contrib import admin
from userauth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class UserAdmin(admin.ModelAdmin):
    list_display=['username','email','phoneno']

admin.site.register(User,UserAdmin)

# Register your models here.
