from django.contrib import admin
from .models import UserProfile, Credential


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('API Keys (Encrypted)', {
            'fields': ('gemini_api_key', 'groq_api_key', 'whatsapp_token'),
            'description': 'API keys are stored encrypted. Use the profile form to set them.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'token_expiry', 'created_at']
    search_fields = ['user__username', 'provider']
    list_filter = ['provider', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Credential Information', {
            'fields': ('user', 'provider', 'scope')
        }),
        ('OAuth2 Tokens (Encrypted)', {
            'fields': ('access_token', 'refresh_token', 'token_expiry'),
            'description': 'Tokens are stored encrypted.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
