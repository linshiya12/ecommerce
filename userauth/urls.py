from django.urls import path,include
from . import views
from .views import resend_otp_view, verify_otp_view

urlpatterns = [
    path('sign-up/',views.register_view,name='sign-up'),
    path('user-login/',views.user_login,name='user-login'),
    path('verify-otp/',views.verify_otp_view, name='verify-otp'),
    path('logout/',views.logout_view,name='logout')
    
]