from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings
import base64


class UserProfile(models.Model):
    """
    Extended user profile to store API keys and credentials.
    API keys are encrypted for security.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # API Keys (encrypted)
    gemini_api_key = models.CharField(max_length=500, blank=True, null=True, help_text="Encrypted Gemini API Key")
    groq_api_key = models.CharField(max_length=500, blank=True, null=True, help_text="Encrypted Groq API Key")
    whatsapp_token = models.CharField(max_length=500, blank=True, null=True, help_text="Encrypted WhatsApp Token")
    
    # Settings
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @staticmethod
    def _get_cipher():
        """Get encryption cipher using SECRET_KEY"""
        key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32].ljust(32, b'0'))
        return Fernet(key)
    
    def encrypt_value(self, value):
        """Encrypt a value"""
        if not value:
            return None
        cipher = self._get_cipher()
        return cipher.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value):
        """Decrypt a value"""
        if not encrypted_value:
            return None
        try:
            cipher = self._get_cipher()
            return cipher.decrypt(encrypted_value.encode()).decode()
        except Exception:
            return None
    
    def set_gemini_key(self, key):
        """Set encrypted Gemini API key"""
        self.gemini_api_key = self.encrypt_value(key)
    
    def get_gemini_key(self):
        """Get decrypted Gemini API key"""
        return self.decrypt_value(self.gemini_api_key) or settings.DEFAULT_GEMINI_API_KEY
    
    def set_groq_key(self, key):
        """Set encrypted Groq API key"""
        self.groq_api_key = self.encrypt_value(key)
    
    def get_groq_key(self):
        """Get decrypted Groq API key"""
        return self.decrypt_value(self.groq_api_key) or settings.DEFAULT_GROQ_API_KEY
    
    def set_whatsapp_token(self, token):
        """Set encrypted WhatsApp token"""
        self.whatsapp_token = self.encrypt_value(token)
    
    def get_whatsapp_token(self):
        """Get decrypted WhatsApp token"""
        return self.decrypt_value(self.whatsapp_token)


class Credential(models.Model):
    """
    Store OAuth2 credentials for Google services.
    Stores refresh tokens to maintain access.
    """
    PROVIDER_CHOICES = [
        ('google', 'Google'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credentials')
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    
    # OAuth2 tokens (encrypted)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    scope = models.TextField(help_text="Space-separated list of scopes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "OAuth Credential"
        verbose_name_plural = "OAuth Credentials"
        unique_together = ['user', 'provider']
    
    def __str__(self):
        return f"{self.user.username} - {self.provider}"
    
    @staticmethod
    def _get_cipher():
        """Get encryption cipher using SECRET_KEY"""
        key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32].ljust(32, b'0'))
        return Fernet(key)
    
    def encrypt_token(self, token):
        """Encrypt a token"""
        if not token:
            return None
        cipher = self._get_cipher()
        return cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token):
        """Decrypt a token"""
        if not encrypted_token:
            return None
        try:
            cipher = self._get_cipher()
            return cipher.decrypt(encrypted_token.encode()).decode()
        except Exception:
            return None
    
    def set_access_token(self, token):
        """Set encrypted access token"""
        self.access_token = self.encrypt_token(token)
    
    def get_access_token(self):
        """Get decrypted access token"""
        return self.decrypt_token(self.access_token)
    
    def set_refresh_token(self, token):
        """Set encrypted refresh token"""
        self.refresh_token = self.encrypt_token(token)
    
    def get_refresh_token(self):
        """Get decrypted refresh token"""
        return self.decrypt_token(self.refresh_token)
