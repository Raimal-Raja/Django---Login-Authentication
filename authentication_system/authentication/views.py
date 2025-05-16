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
            logger.info(f"Registration successful for {user.username}")
            print(f"DEBUG: Registered user {user.username} with email: {user.email}")  # Temporary debug
            messages.success(request, 'Account created successfully! You can now log in.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Registration successful!', 'redirect_url': '/login/'})
            return redirect('login')
        else:
            logger.error(f"Registration failed: {form.errors}")
            print(f"DEBUG: Registration errors: {form.errors}")  # Temporary debug
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
    try:
        profile = request.user.userprofile
        logger.info(f"Profile retrieved for {request.user.username}: bio={profile.bio}")
        print(f"DEBUG: Profile for {request.user.username}: bio={profile.bio}, phone={profile.phone_number}")  # Temporary debug
    except UserProfile.DoesNotExist:
        logger.warning(f"Creating missing UserProfile for user: {request.user.username}")
        profile = UserProfile.objects.create(user=request.user)
        print(f"DEBUG: Created new UserProfile for {request.user.username}")  # Temporary debug

    context = {
        'user': request.user,
        'profile': profile
    }

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'avatar':
            if 'avatar' in request.FILES:
                avatar = request.FILES['avatar']
                valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                ext = os.path.splitext(avatar.name)[1].lower()
                if ext not in valid_extensions:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid file type. Only JPG, PNG, and GIF are allowed.'
                    })
                if avatar.size > 5 * 1024 * 1024:
                    return JsonResponse({
                        'success': False,
                        'error': 'File size too large. Maximum is 5MB.'
                    })
                profile.avatar = avatar
                profile.save()
                logger.info(f"Avatar updated for {request.user.username}")
                print(f"DEBUG: Avatar updated for {request.user.username}")  # Temporary debug
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
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
            profile.bio = request.POST.get('bio', '')
            profile.phone_number = request.POST.get('phone_number', '')
            profile.location = request.POST.get('location', '')
            birth_date = request.POST.get('birth_date')
            profile.birth_date = birth_date if birth_date else None
            profile.website = request.POST.get('website', '')
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()
            logger.info(f"Profile updated for {request.user.username}: bio={profile.bio}")
            print(f"DEBUG: Profile updated for {request.user.username}: bio={profile.bio}")  # Temporary debug
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully!'
            })
            
        elif form_type == 'password':
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
    
    return render(request, 'dashboard.html', context)

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