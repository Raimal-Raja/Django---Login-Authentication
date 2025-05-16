from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserCreationForm, UserProfileForm
from .models import UserProfile
import json
from django.core.exceptions import ValidationError
import os
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'base.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Registration successful!', 'redirect_url': '/login/'})
            return redirect('login')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Please correct the errors below.',
                    'errors': form.errors.as_json()
                })
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Login successful!', 'redirect_url': '/dashboard/'})
            return redirect('dashboard')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Invalid username or password.'})
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@login_required
def dashboard_view(request):
    # Ensure UserProfile exists
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        logger.warning(f"Creating missing UserProfile for user: {request.user.username}")
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'avatar':
            # Handle avatar upload only
            if 'avatar' in request.FILES:
                avatar = request.FILES['avatar']
                # Validate file type and size
                valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                ext = os.path.splitext(avatar.name)[1].lower()
                if ext not in valid_extensions:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid file type. Only JPG, PNG, and GIF are allowed.'
                    })
                if avatar.size > 5 * 1024 * 1024:  # 5MB limit
                    return JsonResponse({
                        'success': False,
                        'error': 'File size too large. Maximum is 5MB.'
                    })
                profile.avatar = avatar
                profile.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Profile picture updated successfully!',
                    'avatar_url': profile.avatar.url
                })
            return JsonResponse({
                'success': False,
                'error': 'No file uploaded.'
            })
            
        elif form_type == 'profile':
            # Update profile information
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            
            try:
                user.full_clean()  # Validate user data
                user.save()
            except ValidationError as e:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid user data: ' + str(e)
                })
            
            profile.bio = request.POST.get('bio', '')
            profile.phone_number = request.POST.get('phone_number', '')
            profile.location = request.POST.get('location', '')
            profile.birth_date = request.POST.get('birth_date')  # Handle date input
            profile.website = request.POST.get('website', '')
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            
            try:
                profile.full_clean()  # Validate profile data
                profile.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Profile updated successfully!'
                })
            except ValidationError as e:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid profile data: ' + str(e)
                })
            
        elif form_type == 'password':
            # Change password
            current_password = request.POST.get('current_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if not request.user.check_password(current_password):
                return JsonResponse({
                    'success': False,
                    'error': 'Your current password was entered incorrectly.'
                })
                
            if new_password1 != new_password2:
                return JsonResponse({
                    'success': False,
                    'error': 'The two password fields didn\'t match.'
                })
                
            if len(new_password1) < 8:
                return JsonResponse({
                    'success': False,
                    'error': 'Password must be at least 8 characters long.'
                })
                
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            return JsonResponse({
                'success': True,
                'message': 'Password changed successfully!'
            })
            
        elif form_type == 'delete':
            # Delete account
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)
            
            if user is not None:
                user.delete()
                return JsonResponse({
                    'success': True,
                    'message': 'Your account has been deleted successfully.',
                    'redirect_url': '/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid password. Account deletion failed.'
                })
    
    return render(request, 'dashboard.html', {'user': request.user})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'You have been logged out successfully.', 'redirect_url': '/'})
    return redirect('home')

@csrf_exempt
def check_username_availability(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        available = not User.objects.filter(username=username).exists()
        return JsonResponse({'available': available})
    return JsonResponse({'available': False})