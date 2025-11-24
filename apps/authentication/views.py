from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import SignUpForm
from apps.main.models import Customer
from apps.profiles.models import Profile
from apps.cart.utils import transfer_guest_cart_to_user


def signup_view(request):
    """Handle user sign up"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create associated Customer profile
            Customer.objects.create(user=user)
            
            # Create or update Profile with account type
            account_type = form.cleaned_data.get('account_type', 'BUYER')
            first_name = form.cleaned_data.get('first_name', '')
            last_name = form.cleaned_data.get('last_name', '')
            email = form.cleaned_data.get('email', '')
            
            profile, created = Profile.objects.get_or_create(user=user)
            profile.account_type = account_type
            profile.first_name = first_name
            profile.last_name = last_name
            profile.email = email
            profile.save()
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('auth:login')
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})


def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Transfer guest cart to user cart
                transfer_guest_cart_to_user(request)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'authentication/login.html', {'form': form})


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# JSON API endpoints for Flutter
@csrf_exempt
def login_json(request):
    """Handle user login for Flutter (JSON response)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return JsonResponse({
                        "status": True,
                        "username": user.username,
                        "message": "Login successful!"
                    }, status=200)
                else:
                    return JsonResponse({
                        "status": False,
                        "message": "Account is disabled."
                    }, status=401)
            else:
                return JsonResponse({
                    "status": False,
                    "message": "Invalid username or password."
                }, status=401)
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=400)
    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=405)


@csrf_exempt
def signup_json(request):
    """Handle user sign up for Flutter (JSON response)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password1 = data.get('password1')
            password2 = data.get('password2')
            email = data.get('email', '')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            account_type = data.get('account_type', 'BUYER')
            
            # Validate passwords match
            if password1 != password2:
                return JsonResponse({
                    "status": False,
                    "message": "Passwords do not match."
                }, status=400)
            
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    "status": False,
                    "message": "Username already exists."
                }, status=400)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                password=password1,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create associated Customer profile
            Customer.objects.create(user=user)
            
            # Create or update Profile with account type
            profile, created = Profile.objects.get_or_create(user=user)
            profile.account_type = account_type
            profile.first_name = first_name
            profile.last_name = last_name
            profile.email = email
            profile.save()
            
            return JsonResponse({
                "status": True,
                "username": user.username,
                "message": "User created successfully!"
            }, status=200)
            
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=400)
    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=405)


@csrf_exempt
def logout_json(request):
    """Handle user logout for Flutter (JSON response)"""
    if request.method == 'POST':
        try:
            username = request.user.username
            logout(request)
            return JsonResponse({
                "status": True,
                "username": username,
                "message": "Logout successful!"
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=400)
    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=405)

