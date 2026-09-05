from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from accounts.models import UserProfile, Credential
from workflows.services.google_service import GoogleOAuthService
from django.utils import timezone
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation
        if not all([username, email, password, password_confirm]):
            messages.error(request, 'All fields are required')
            return render(request, 'accounts/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'accounts/register.html')
        
        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            UserProfile.objects.create(user=user)
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
        
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            messages.error(request, 'Registration failed. Please try again.')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'accounts/login.html')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('home')


@login_required
def profile_view(request):
    """User profile view for managing API keys"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update API keys
        gemini_key = request.POST.get('gemini_api_key')
        groq_key = request.POST.get('groq_api_key')
        whatsapp_token = request.POST.get('whatsapp_token')
        
        if gemini_key:
            profile.set_gemini_key(gemini_key)
        
        if groq_key:
            profile.set_groq_key(groq_key)
        
        if whatsapp_token:
            profile.set_whatsapp_token(whatsapp_token)
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    # Check Google connection status
    google_connected = Credential.objects.filter(user=request.user, provider='google').exists()
    
    context = {
        'profile': profile,
        'google_connected': google_connected,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def google_connect_view(request):
    """Initiate Google OAuth2 flow"""
    oauth_service = GoogleOAuthService(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    
    # Generate state for CSRF protection
    state = str(request.user.id)
    
    # Get authorization URL
    auth_url = oauth_service.get_authorization_url(state=state)
    
    return redirect(auth_url)


@login_required
def google_callback_view(request):
    """Handle Google OAuth2 callback"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f'Google authorization failed: {error}')
        return redirect('profile')
    
    if not code:
        messages.error(request, 'No authorization code received')
        return redirect('profile')
    
    # Verify state (simple check)
    if state != str(request.user.id):
        messages.error(request, 'Invalid state parameter')
        return redirect('profile')
    
    # Exchange code for tokens
    oauth_service = GoogleOAuthService(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    
    result = oauth_service.exchange_code_for_tokens(code)
    
    if result.get('success'):
        # Store credentials
        credential, created = Credential.objects.get_or_create(
            user=request.user,
            provider='google',
            defaults={
                'scope': ' '.join(result.get('scopes', []))
            }
        )
        
        credential.set_access_token(result['access_token'])
        if result.get('refresh_token'):
            credential.set_refresh_token(result['refresh_token'])
        
        if result.get('token_expiry'):
            credential.token_expiry = datetime.fromisoformat(result['token_expiry'])
        
        credential.scope = ' '.join(result.get('scopes', []))
        credential.save()
        
        messages.success(request, 'Google account connected successfully!')
    else:
        messages.error(request, f"Failed to connect Google account: {result.get('error')}")
    
    return redirect('profile')


@login_required
def google_disconnect_view(request):
    """Disconnect Google account"""
    if request.method == 'POST':
        Credential.objects.filter(user=request.user, provider='google').delete()
        messages.success(request, 'Google account disconnected')
    
    return redirect('profile')


def home_view(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return render(request, 'home.html')
