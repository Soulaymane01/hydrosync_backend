from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import login_view, logout_view, current_user_view, UserListCreateView, UserDetailView , MeterViewSet, MeterReadingViewSet, DashboardView, receive_esp32_data
from .client_views import ClientLoginView, ClientLogoutView, ClientMeView


# Create router and register viewsets
router = DefaultRouter()
router.register(r'meters', MeterViewSet, basename='meter')
router.register(r'readings', MeterReadingViewSet, basename='reading')

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
  
    # Router URLs
    path('', include(router.urls)),
    
    # Dashboard endpoint
    path('dashboard/overview/', DashboardView.as_view(), name='dashboard-overview'),
    
    # ESP32 data receiver endpoint
    path('esp32/data/', receive_esp32_data, name='esp32-data'),
]