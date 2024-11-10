 # Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.core.mail import send_mail
from django.conf import settings
import random
import re
from phonenumber_field.modelfields import PhoneNumberField


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

def verify_otp_view(request):
    if request.method == "POST":
        # email = request.POST.get("email")
        otp = request.POST.get("otp")

        # user_verification = get_object_or_404(EmailVerification, user__email=email)
        temp_user_data = request.session.pop('temp_user', None)
        
        if temp_user_data["otp"] == int(otp):
            # user_verification.is_verified = True
            
            # Retrieve the temporary user data from the session
            
            if temp_user_data:
                user = User(
                    username=temp_user_data['username'],
                    email=temp_user_data['email'],
                    phoneno=temp_user_data['phoneno']
                )
                user.set_password(temp_user_data['password'])  # Hash the password
                user.save()  # Now save the user to the database

            messages.success(request, "Your email has been verified. You can now log in.")
            return redirect("/user-login")
        else:
            messages.warning(request, "Invalid OTP. Please try again.")
            return redirect("verify-otp")

    return render(request, "emailotp.html")

# User registration
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmpassword = request.POST.get("confirmpassword")
        phoneno = request.POST.get("phoneno")

        # Checking required fields
        if not all([username, email, password, confirmpassword, phoneno]):
            messages.warning(request, "All fields are required.")
            return redirect("/sign-up")
        
        # Checking matching password
        if password != confirmpassword:
            messages.warning(request, "Passwords do not match.")
            return redirect("/sign-up")
        
        # Checking password strength
        if not strong_password(password):
            messages.warning(request, "Password must be at least 8 characters long, "
                                      "include an uppercase letter, a lowercase letter, "
                                      "a digit, and a special character.")
            return redirect("/sign-up")
        
        # Save user 
        try:
            otp = random.randint(100000, 999999)
    
            # Send OTP email
            send_mail(
                'Your OTP Code',
                f'Your OTP code is: {otp}. Please enter this code to verify your email.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, "Signup successful! An OTP has been sent to your email. Please verify.")
            
            # Store user data temporarily in the session
            request.session['temp_user'] = {
                'username': username,
                'email': email,
                'phoneno': phoneno,
                'password': password,
                'otp':otp
            }
            return redirect("/verify-otp")

        # Checking field constraints    
        except IntegrityError as e:
            if "username" in str(e):
                messages.warning(request, "Username is already taken.")
            elif "email" in str(e):
                messages.warning(request, "Email is already registered.")
            elif "phoneno" in str(e):
                messages.warning(request, "Phone number is already registered.")
            return redirect("/sign-up")
        except Exception as e:
            messages.warning(request, f"An unexpected error occurred: {str(e)}")
            return redirect("/sign-up")

    return render(request, "loginsignup.html")

def resend_otp_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        # Get the user associated with the email
        user = get_object_or_404(User, email=email)
        
        # Generate a new OTP
        new_otp = random.randint(100000, 999999)  # Example OTP range
        EmailVerification.objects.filter(user=user).update(otp=new_otp)  # Update existing OTP
        
        # Send OTP to user's email
        send_mail(
            'Your OTP Code',
            f'Your OTP code is: {new_otp}',
            settings.DEFAULT_FROM_EMAIL,  # Use the default email
            [email],  # Recipient email
            fail_silently=False,
        )
        
        messages.success(request, "A new OTP has been sent to your email.")
        return redirect('/verify-otp/')
    
    return render(request, "emailotp.html")

# google authentication


# User login
def user_login(request):
    # if request.user.is_authenticated:
    #     return redirect("/home")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:
            # print("user is not none")
            login(request, user)
            return redirect("/")
        else:
            print("invalid email or password")
            messages.info(request, "Invalid email or password")
            return redirect("/user-login")
    print("its not a post method")
    return render(request, "login.html")

# logout function
def logout_view(request):
    logout(request)
    return redirect("/user-login")

