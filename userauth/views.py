 # Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from .models import User
from user.models import *
from django.core.mail import send_mail
from django.conf import settings
import random
import re
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from datetime import timedelta
import string
from django.views.decorators.cache import never_cache

# To check password strength
def strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


def generate_referral_code(length=8):
    characters = string.ascii_uppercase + string.digits
    referral_code = ''.join(random.choices(characters, k=length))
    return referral_code


def verify_otp_view(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        temp_user_data = request.session.pop('temp_user', None)

        if temp_user_data:
            otp_created_at = timezone.datetime.fromisoformat(temp_user_data["otp_created_at"])
            current_time = timezone.now()
            otp_expiry_time = otp_created_at + timedelta(minutes=1)

            # Check if OTP has expired
            if current_time > otp_expiry_time:
                request.session['message'] = "OTP has expired. Please request a new OTP."
                request.session['message_type'] = "danger"
                return redirect("verify-otp")

            referral_code = generate_referral_code()
            # Check if OTP entered is correct
            if temp_user_data["otp"] == int(otp):
                user = User(
                    username=temp_user_data['username'],
                    email=temp_user_data['email'],
                    phoneno=temp_user_data['phoneno'],
                    referral_code=referral_code
                )
                user.set_password(temp_user_data['password'])
                user.save()
                
                # referralcode
                referral=temp_user_data["referral_code"]
                if referral:
                    referrer = User.objects.filter(referral_code=referral).first()
                    if referrer:
                        # Add referral bonus to the referrer user's wallet
                        referrer_wallet, created = Wallet.objects.get_or_create(user=referrer)
                        referrer_wallet.add_to_wallet(100) 


                new_user_wallet, created = Wallet.objects.get_or_create(user=user)
                new_user_wallet.add_to_wallet(50)

                request.session['message'] = "Your email has been verified. You can now log in."
                request.session['message_type'] = "success"
                return redirect("/user-login")
            else:
                # Store the otp_created_at value in session again for invalid OTP
                request.session['message'] = "Invalid OTP. Please try again."
                request.session['message_type'] = "danger"
                
                # Preserve the temp user data including otp_created_at
                request.session['temp_user'] = {
                    'username': temp_user_data['username'],
                    'email': temp_user_data['email'],
                    'phoneno': temp_user_data['phoneno'],
                    'password': temp_user_data['password'],
                    'otp': temp_user_data['otp'],
                    'otp_created_at': temp_user_data['otp_created_at'],  # Make sure to preserve this
                }

                return redirect("verify-otp")

    # Get message from session and pop it
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    # Get otp_created_at value
    otp_created_at = request.session.get('temp_user', {}).get('otp_created_at', None)

    context = {
        "message": message,
        "message_type": message_type,
        "otp_created_at": otp_created_at,
    }

    return render(request, "emailotp.html", context)


# User registration
@never_cache
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmpassword = request.POST.get("confirmpassword")
        phoneno = request.POST.get("phoneno")
        referral_code=request.POST.get("referral_code")

        if referral_code:
            pass  
        else:
            referral_code = None

        # Checking required fields
        if not all([username, email, password, confirmpassword, phoneno]):
            messages.warning(request, "All fields are required.")
            request.session['message'] = "All fields are required."
            request.session['message_type'] = "warning"
            return redirect("/sign-up")
        
        if " " in username:
            request.session['message'] = "Username cannot contain spaces."
            request.session['message_type'] = "warning"
            return redirect("/sign-up")
        
        if len(username) < 4 or len(username) > 20:
            request.session['message'] = "Username must be between 4 and 20 characters."
            request.session['message_type'] = "warning"
            return redirect("/sign-up")

        # Checking matching password
        if password != confirmpassword:
            request.session['message'] = "Passwords do not match."
            request.session['message_type'] = "warning"
            return redirect("/sign-up")
        
        # Checking password strength
        if not strong_password(password):
            request.session['message'] = """Password must be at least 8 characters long,
                                        include an uppercase letter, a lowercase letter,
                                        a digit, and a special character."""
            request.session['message_type'] = "warning"
            return redirect("/sign-up")
        
        # Save user 
        try:
            otp = random.randint(100000, 999999)
            otp_created_at = timezone.now().isoformat()
    
            # Send OTP email
            send_mail(
                'Your OTP Code',
                f'Your OTP code is: {otp}. Please enter this code to verify your email.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            request.session['message'] = "Signup successful! An OTP has been sent to your email. Please verify."
            request.session['message_type'] = "success"
        
            # Store user data temporarily in the session
            request.session['temp_user'] = {
                'username': username,
                'email': email,
                'phoneno': phoneno,
                'password': password,
                'otp':otp,
                'otp_created_at': otp_created_at,
                'referral_code' :referral_code

            }
            return redirect("/verify-otp")

        # Checking field constraints    
        except IntegrityError as e:
            if "username" in str(e):
                request.session['message'] = "Username is already taken."
                request.session['message_type'] = "warning"
                
            elif "email" in str(e):
                request.session['message'] = "Email is already registered."
                request.session['message_type'] = "warning"
               
            elif "phoneno" in str(e):
                request.session['message'] = "Phone number is already registered."
                request.session['message_type'] = "warning"
            return redirect("/sign-up")
        except Exception as e:
            request.session['message'] = f"An unexpected error occurred: {str(e)}"
            request.session['message_type'] = "danger"
            return redirect("/sign-up")
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "message": message,
        "message_type": message_type,
    }    
    return render(request, "loginsignup.html",context)

def resend_otp_view(request):
    temp_user = request.session.get('temp_user')
    email =(temp_user.get('email'))

    if request.method == "GET":
        # Generate a new OTP
        new_otp = random.randint(100000, 999999)  # Example OTP range
        otp_created_at = timezone.now().isoformat()

        # Send OTP to user's email
        send_mail(
            'Your OTP Code',
            f'Your new OTP code is: {new_otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        # Update session data with the new OTP
        request.session['temp_user']['otp'] = new_otp
        request.session['temp_user']['otp_created_at'] = otp_created_at

        # Optional: Flash a success message
        request.session['message'] = "A new OTP has been sent to your email."
        request.session['message_type'] = "success"

        # Redirect to OTP verification page
        return redirect('verify-otp')

    # If the method is GET or no valid condition matches
    return redirect('verify-otp')

# User login
@never_cache
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            request.session['message'] = "Login successful!"
            request.session['message_type'] = "success"
            return redirect("/")
        else:
            request.session['message'] =  "Invalid email or password"
            request.session['message_type'] = "info"
            return redirect("/user-login")
    
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "message": message,
        "message_type": message_type,
    }    
    return render(request, "login.html",context)

# logout function
def logout_view(request):
    logout(request)
    return redirect("/user-login")


# forgot password

otp_dict={}
def forgot_pass(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email:
            request.session['message'] =  "Please enter your email address."
            request.session['message_type'] = "info"
            return redirect("/forgot")
        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)

            otp_dict[email] = {
                'otp': otp,
                'expiry': timezone.now() + timedelta(minutes=10)  # OTP expires in 10 minutes
            }

            send_mail(
                'Your OTP Code',
                f'Your OTP code is: {otp}. Please enter this code to verify your email.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            request.session['email'] = email

            request.session['message'] =  'OTP sent to your email address. Please check your inbox.'
            request.session['message_type'] = "success"
            return redirect('/forgot-otp') 

        except User.DoesNotExist:
            request.session['message'] =  'email address not registered'
            request.session['message_type'] = "error"
            return redirect("/forgot")

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "message": message,
        "message_type": message_type,
    }    
    return render(request,'forgotpass.html',context)

# forgot password OTP verification

def forgot_otp_view(request):
    if request.method == 'POST':
        email = request.session.get('email')  # Retrieve email from session
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check if email exists in session and OTP is valid
        if not email:
            request.session['message'] = 'Session expired. Please request a new OTP.'
            request.session['message_type'] = "error"
            return redirect('forgot-otp')
        # Verify OTP and ensure it is valid and not expired
        if otp_dict[email]['otp'] == int(otp):
            if timezone.now() > otp_dict[email]['expiry']:
                request.session['message'] = 'OTP has expired. Please request a new one.'
                request.session['message_type'] = "error"
                return redirect('forgot-otp')
            
            if not strong_password(new_password):
                request.session['message'] = """Password must be at least 8 characters long,
                                            include an uppercase letter, a lowercase letter,
                                            a digit, and a special character."""
                request.session['message_type'] = "warning"
                return redirect('forgot-otp')
            
            # Check if passwords match
            if new_password != confirm_password:
                request.session['message'] = 'Passwords do not match.'
                request.session['message_type'] = "error"
                return redirect('forgot-otp')
            
            #password resetting
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request,user)
            
            # Remove the OTP from the dictionary
            del otp_dict[email]
       
            request.session['message'] = 'Your password has been successfully reset.'
            request.session['message_type'] = "success"
            return redirect('user-login')  
        
        else:
            request.session['message'] = 'Invalid OTP. Please try again.'
            request.session['message_type'] = "error"
            return redirect('forgot-otp')

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "message": message,
        "message_type": message_type,
    }    
    return render(request,"forgototp.html",context)

@login_required(login_url="user-login")
def Reset_pass(request):
    user = request.user
    if request.method=="POST":
        old_password=request.POST.get("old_password")
        new_password=request.POST.get("new_password")
        conf_new_password=request.POST.get("conf_new_password")

        if not all([old_password,new_password,conf_new_password]):
            request.session['message']="All fields are required."
            request.session['message_type']="warning"
            return redirect("/reset")

        if new_password != conf_new_password:
            request.session['message'] = "password does not match"
            request.session['message_type'] = "error"
            return redirect("/reset")

        if not strong_password(new_password):
            request.session['message'] = """Password must be at least 8 characters long,
                                        include an uppercase letter, a lowercase letter,
                                        a digit, and a special character."""
            request.session['message_type'] = "warning"
            return redirect("/reset")

        if check_password(old_password,user.password):
            user.set_password(new_password)
            user.save()
            request.session['message']="password changed successfully"
            request.session['message_type']="success"
            return redirect("/reset")
        else:
            request.session['message']="old password is incorrect"
            request.session['message_type']="danger"
            return redirect("/reset")

        

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "message": message,
        "message_type": message_type,
    }    
 
    return render(request,"reset.html",context)


import requests
import secrets
import urllib.parse

def google_login(request):
    google_client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri ='http://127.0.0.1:8000/google/callback/'
    scope = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
    state = secrets.token_urlsafe(16)
    params =  {
        'client_id':google_client_id,
        'redirect_uri':redirect_uri,
        'response_type':'code',
        'scope': scope,
        'state':state,
        'access_type':'offline',
        'prompt':'select_account'
    }
    request.session['state'] = state
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
   
    return redirect(url)



def google_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    request_state = request.session.pop('state')
    if error or request_state != state :
        request.session['message'] = 'Error'
        return redirect('login')
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'code': code ,
        'client_id' : settings.GOOGLE_CLIENT_ID,
        'client_secret' :settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri":'http://127.0.0.1:8000/google/callback/',
        'grant_type':'authorization_code'
    }
    token_response = requests.post(token_url,data=token_data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')


    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    user_info_params = {'access_token':access_token}
    user_info_response = requests.get(user_info_url,params=user_info_params)
    user_info = user_info_response.json()


    email = str(user_info.get('email'))
    
   
    username = email.split('@')[0]

    user , created = User.objects.get_or_create(email=email , defaults={
        'username':username,
    })

    if created :
        user.set_unusable_password()
    user.save()
    login(request,user)
    return redirect('home')



