from django.urls import path,include
from . import views
from .views import resend_otp_view, verify_otp_view

urlpatterns = [
    path('sign-up/',views.register_view,name='sign-up'),
    path('user-login/',views.user_login,name='user-login'),
    path('verify-otp/',views.verify_otp_view, name='verify-otp'),
    path('forgot-otp/',views.forgot_otp_view, name='forgot-otp'),
    path('forgot/',views.forgot_pass, name='forgot'),
    path('logout/',views.logout_view,name='logout'),
    path('reset/',views.Reset_pass,name="resetpass"),
    path('resendotp/',views.resend_otp_view,name="resendotp"),
    path('google-login',views.google_login,name='google_login'),
    path('google/callback/',views.google_callback,name="google_callback")
    
    
]