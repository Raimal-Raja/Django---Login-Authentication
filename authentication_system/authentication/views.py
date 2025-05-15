from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserCreationForm, UserProfileForm
import json

def home(request):
    return render(request, 'base.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
        else:
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
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@login_required
def dashboard_view(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            # Update profile information
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
            profile = user.userprofile
            profile.bio = request.POST.get('bio', '')
            profile.phone_number = request.POST.get('phone_number', '')
            profile.location = request.POST.get('location', '')
            
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
            
        elif form_type == 'password':
            # Change password
            current_password = request.POST.get('current_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if not request.user.check_password(current_password):
                messages.error(request, 'Your current password was entered incorrectly.')
                return redirect('dashboard#security')
                
            if new_password1 != new_password2:
                messages.error(request, 'The two password fields didn\'t match.')
                return redirect('dashboard#security')
                
            if len(new_password1) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
                return redirect('dashboard#security')
                
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully!')
            return redirect('dashboard#security')
            
        elif form_type == 'delete':
            # Delete account
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)
            
            if user is not None:
                user.delete()
                messages.success(request, 'Your account has been deleted successfully.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid password. Account deletion failed.')
                return redirect('dashboard#delete')
    
    return render(request, 'dashboard.html', {'user': request.user})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@csrf_exempt
def check_username_availability(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        available = not User.objects.filter(username=username).exists()
        return JsonResponse({'available': available})
    return JsonResponse({'available': False})