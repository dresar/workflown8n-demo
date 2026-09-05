from django.urls import path
from accounts import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('google/connect/', views.google_connect_view, name='google_connect'),
    path('google/callback/', views.google_callback_view, name='google_callback'),
    path('google/disconnect/', views.google_disconnect_view, name='google_disconnect'),
]

