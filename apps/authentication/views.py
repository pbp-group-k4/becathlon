from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import SignUpForm
from apps.main.models import Customer
from apps.profiles.models import Profile
from apps.cart.utils import transfer_guest_cart_to_user


def signup_view(request):
    """Handle user sign up for web"""
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
    """Handle user login for web"""
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
    """Handle user logout for web"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# Flutter Mobile API Views (following PBP tutorial pattern)
@csrf_exempt
def flutter_login(request):
    """Handle Flutter app login - following PBP tutorial pattern"""
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    
    if user is not None:
        if user.is_active:
            login(request, user)
            # Login status successful
            return JsonResponse({
                "username": user.username,
                "status": True,
                "message": "Login successful!"
            }, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "Login failed, account is disabled."
            }, status=401)
    else:
        return JsonResponse({
            "status": False,
            "message": "Login failed, please check your username or password."
        }, status=401)


@csrf_exempt
def flutter_register(request):
    """Handle Flutter app registration"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2')
        
        # Validation
        if not username or not password:
            return JsonResponse({
                'status': False,
                'message': 'Username and password are required'
            }, status=400)
        
        if password != password2:
            return JsonResponse({
                'status': False,
                'message': 'Passwords do not match'
            }, status=400)
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'status': False,
                'message': 'Username already exists'
            }, status=400)
        
        # Create user
        user = User.objects.create_user(username=username, password=password)
        
        # Create customer profile
        Customer.objects.create(user=user)
        
        # Profile is created by signal, so get and update it
        profile, created = Profile.objects.get_or_create(user=user)
        profile.account_type = 'BUYER'
        profile.save()
        
        return JsonResponse({
            'status': True,
            'message': 'Registration successful!',
            'username': username
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
def flutter_logout(request):
    """Handle Flutter app logout"""
    try:
        logout(request)
        return JsonResponse({
            'status': True,
            'message': 'Logout successful'
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': str(e)
        }, status=500)
