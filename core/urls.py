from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeterViewSet, MeterReadingViewSet, DashboardView, receive_esp32_data

# Create router and register viewsets
router = DefaultRouter()
router.register(r'meters', MeterViewSet, basename='meter')
router.register(r'readings', MeterReadingViewSet, basename='reading')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Dashboard endpoint
    path('dashboard/overview/', DashboardView.as_view(), name='dashboard-overview'),
    
    # ESP32 data receiver endpoint
    path('esp32/data/', receive_esp32_data, name='esp32-data'),
]
