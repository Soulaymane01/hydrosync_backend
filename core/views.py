# views.py
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, Avg, Max, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import MeterReadings, Meters, Customers, Users
from .serializers import (
    MeterSerializer, 
    MeterReadingSerializer, 
    RealtimeReadingSerializer,
    DashboardStatsSerializer,
    LoginSerializer, 
    UserSerializer, 
    UserCreateSerializer
)


class MeterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing water meters
    """
    queryset = Meters.objects.all()
    serializer_class = MeterSerializer
    
    @action(detail=True, methods=['get'])
    def consumption(self, request, pk=None):
        """Get consumption history for a specific meter"""
        meter = self.get_object()
        days = int(request.query_params.get('days', 7))
        
        start_date = timezone.now() - timedelta(days=days)
        readings = MeterReadings.objects.filter(
            meter=meter,
            reading_date__gte=start_date
        ).order_by('reading_date')
        
        serializer = MeterReadingSerializer(readings, many=True)
        return Response(serializer.data)


class MeterReadingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for meter readings with real-time data support
    """
    queryset = MeterReadings.objects.all()
    serializer_class = MeterReadingSerializer
    
    def get_queryset(self):
        queryset = MeterReadings.objects.all()
        
        # Filter by meter_id if provided
        meter_id = self.request.query_params.get('meter_id', None)
        if meter_id:
            queryset = queryset.filter(meter__meter_id=meter_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(reading_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(reading_date__lte=end_date)
        
        return queryset.order_by('-reading_date')
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the latest readings for all meters"""
        limit = int(request.query_params.get('limit', 10))
        readings = MeterReadings.objects.order_by('-reading_date')[:limit]
        serializer = RealtimeReadingSerializer(readings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def realtime(self, request):
        """Get real-time data (last 24 hours)"""
        hours = int(request.query_params.get('hours', 24))
        start_time = timezone.now() - timedelta(hours=hours)
        
        readings = MeterReadings.objects.filter(
            reading_date__gte=start_time
        ).order_by('reading_date')
        
        serializer = RealtimeReadingSerializer(readings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get aggregated statistics"""
        hours = int(request.query_params.get('hours', 24))
        start_time = timezone.now() - timedelta(hours=hours)
        
        stats = MeterReadings.objects.filter(
            reading_date__gte=start_time
        ).aggregate(
            total=Sum('reading_value'),
            average=Avg('reading_value'),
            max_reading=Max('reading_value'),
            count=Count('id')
        )
        
        return Response(stats)


class DashboardView(APIView):
    """
    API view for dashboard overview with aggregated statistics
    """
    
    def get(self, request):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        
        # Get latest reading
        latest_reading = MeterReadings.objects.order_by('-reading_date').first()
        current_reading = latest_reading.reading_value if latest_reading else Decimal('0.000')
        
        # Today's statistics
        today_readings = MeterReadings.objects.filter(
            reading_date__gte=today_start
        )
        
        today_stats = today_readings.aggregate(
            total=Sum('reading_value'),
            count=Count('id')
        )
        
        total_today = today_stats['total'] or Decimal('0.000')
        readings_count_today = today_stats['count'] or 0
        
        # Calculate average hourly consumption
        hours_elapsed = (now - today_start).total_seconds() / 3600
        average_hourly = total_today / Decimal(str(hours_elapsed)) if hours_elapsed > 0 else Decimal('0.000')
        
        # Yesterday's statistics
        yesterday_readings = MeterReadings.objects.filter(
            reading_date__gte=yesterday_start,
            reading_date__lt=today_start
        )
        
        total_yesterday = yesterday_readings.aggregate(
            total=Sum('reading_value')
        )['total'] or Decimal('0.000')
        
        # Calculate change percentage with edge case handling
        # Minimum threshold for meaningful comparison (10 liters)
        MIN_THRESHOLD = Decimal('10.0')
        MAX_PERCENTAGE = Decimal('999.0')
        
        comparison_reliable = True
        
        if total_yesterday > MIN_THRESHOLD:
            # Normal calculation
            change_percentage = ((total_today - total_yesterday) / total_yesterday) * 100
            
            # Cap extreme percentages
            if change_percentage > MAX_PERCENTAGE:
                change_percentage = MAX_PERCENTAGE
            elif change_percentage < -MAX_PERCENTAGE:
                change_percentage = -MAX_PERCENTAGE
        elif total_yesterday > 0:
            # Yesterday's data exists but is too low for reliable comparison
            change_percentage = ((total_today - total_yesterday) / total_yesterday) * 100
            
            # Cap the percentage
            if change_percentage > MAX_PERCENTAGE:
                change_percentage = MAX_PERCENTAGE
            elif change_percentage < -MAX_PERCENTAGE:
                change_percentage = -MAX_PERCENTAGE
            
            # Mark as unreliable
            comparison_reliable = False
        else:
            # No data from yesterday
            if total_today > 0:
                change_percentage = MAX_PERCENTAGE  # Maximum increase
                comparison_reliable = False
            else:
                change_percentage = Decimal('0.00')
                comparison_reliable = False
        
        # Active meters count
        active_meters = Meters.objects.filter(status='active').count()
        
        # Prepare response data
        stats_data = {
            'current_reading': current_reading,
            'total_today': total_today,
            'average_hourly': average_hourly,
            'total_yesterday': total_yesterday,
            'change_percentage': change_percentage,
            'comparison_reliable': comparison_reliable,
            'active_meters': active_meters,
            'total_readings_today': readings_count_today
        }
        
        serializer = DashboardStatsSerializer(stats_data)
        return Response(serializer.data)


@api_view(['POST'])
def receive_esp32_data(request):
    """
    Endpoint to receive data from ESP32 flowmeter
    Expected JSON format:
    {
        "meter_id": "METER-001",
        "reading_value": 1.234,
        "unit": "L",
        "reading_type": "automatic"
    }
    """
    try:
        meter_id = request.data.get('meter_id')
        reading_value = request.data.get('reading_value')
        unit = request.data.get('unit', 'L')
        reading_type = request.data.get('reading_type', 'automatic')
        
        # Find the meter
        try:
            meter = Meters.objects.get(meter_id=meter_id)
        except Meters.DoesNotExist:
            return Response(
                {'error': f'Meter {meter_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create the reading
        reading = MeterReadings.objects.create(
            meter=meter,
            reading_value=reading_value,
            unit=unit,
            reading_date=timezone.now(),
            reading_type=reading_type,
            anomaly_detected=False,
            usage_status='normal',
            quality_status='good',
            created_at=timezone.now()
        )
        
        # Update meter's last reading
        meter.last_reading = reading_value
        meter.last_reading_date = reading.reading_date
        meter.save()
        
        serializer = MeterReadingSerializer(reading)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
"""
API views for authentication and user management
"""

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login endpoint - Returns JWT tokens and user data
    POST /api/auth/login
    Body: {"email": "user@example.com", "password": "password"}
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'success': False, 'message': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = serializer.validated_data['user']
    
    # Update last login
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    # Serialize user data
    user_serializer = UserSerializer(user)
    user_data = user_serializer.data
    
    # Add role information in frontend-compatible format
    user_data['role'] = {
        'id': user.role.name,  # Use role name as id for frontend compatibility
        'name': get_role_display_name(user.role.name),
        'level': user.role.permission.get('level', 0) if user.role.permission else 0,
        'description': user.role.description,
    }
    
    # Format permissions for frontend
    user_data['permissions'] = [
        {
            'id': f"{perm['resource']}_{perm['action']}",
            'name': f"{perm['resource'].title()} {perm['action'].title()}",
            'resource': perm['resource'],
            'action': perm['action'],
            'description': f"{perm['action'].title()} access to {perm['resource']}"
        }
        for perm in user_data['permissions']
    ]
    
    return Response({
        'success': True,
        'token': access_token,
        'refresh': refresh_token,
        'user': user_data,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout endpoint - Blacklists the refresh token
    POST /api/auth/logout
    Headers: Authorization: Bearer <token>
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Get current user endpoint
    GET /api/auth/me
    Headers: Authorization: Bearer <token>
    """
    user = request.user
    
    try:
        # Get the Users object (not Django auth_user)
        partner_user = Users.objects.select_related('role').get(email=user.email)
        serializer = UserSerializer(partner_user)
        user_data = serializer.data
        
        # Format for frontend compatibility
        user_data['role'] = {
            'id': partner_user.role.name,
            'name': get_role_display_name(partner_user.role.name),
            'level': partner_user.role.permission.get('level', 0) if partner_user.role.permission else 0,
            'description': partner_user.role.description,
        }
        
        # Format permissions
        user_data['permissions'] = [
            {
                'id': f"{perm['resource']}_{perm['action']}",
                'name': f"{perm['resource'].title()} {perm['action'].title()}",
                'resource': perm['resource'],
                'action': perm['action'],
                'description': f"{perm['action'].title()} access to {perm['resource']}"
            }
            for perm in user_data['permissions']
        ]
        
        return Response({
            'success': True,
            'user': user_data
        }, status=status.HTTP_200_OK)
    except Users.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


class UserListCreateView(generics.ListCreateAPIView):
    """
    GET /api/users - List all users
    POST /api/users - Create new user
    """
    queryset = Users.objects.filter(deleted_at__isnull=True).select_related('role')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response({
            'success': True,
            'users': serializer.data
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            return Response({
                'success': True,
                'message': 'User created successfully',
                'user': user_data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/users/:id - Get user details
    PUT /api/users/:id - Update user
    DELETE /api/users/:id - Delete user (soft delete)
    """
    queryset = Users.objects.filter(deleted_at__isnull=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete user"""
        user = self.get_object()
        user.deleted_at = timezone.now()
        user.status = 'inactive'
        user.save(update_fields=['deleted_at', 'status', 'updated_at'])
        
        return Response({
            'success': True,
            'message': 'User deleted successfully'
        }, status=status.HTTP_200_OK)


def get_role_display_name(role_name):
    """Convert role name to display name"""
    role_names = {
        'admin': 'System Administrator',
        'manager': 'Operations Manager',
        'technician': 'Field Technician',
        'operator': 'System Operator',
        'customer_service': 'Customer Service',
        'viewer': 'Read-Only User',
    }
    return role_names.get(role_name, role_name.replace('_', ' ').title())
