"""
URL configuration for core app - Authentication and user management endpoints
"""
from django.urls import path
from .views import (
    login_view, logout_view, current_user_view, UserListCreateView, UserDetailView
)
from .client_views import ClientLoginView, ClientLogoutView, ClientMeView

urlpatterns = [
    # Partner Auth
    path('auth/login', login_view, name='login'),
    path('auth/logout', logout_view, name='logout'),
    path('auth/me', current_user_view, name='me'),

    # Client Auth
    path('client/auth/login', ClientLoginView.as_view(), name='client-login'),
    path('client/auth/logout', ClientLogoutView.as_view(), name='client-logout'),
    path('client/auth/me', ClientMeView.as_view(), name='client-me'),

    # User Management
    path('users', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<uuid:pk>', UserDetailView.as_view(), name='user-detail'),
]
