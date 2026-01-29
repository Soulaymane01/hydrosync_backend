# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Avg, Max, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import MeterReadings, Meters, Customers
from .serializers import (
    MeterSerializer, 
    MeterReadingSerializer, 
    RealtimeReadingSerializer,
    DashboardStatsSerializer
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
        
        # Calculate change percentage
        if total_yesterday > 0:
            change_percentage = ((total_today - total_yesterday) / total_yesterday) * 100
        else:
            change_percentage = Decimal('0.00')
        
        # Active meters count
        active_meters = Meters.objects.filter(status='active').count()
        
        # Prepare response data
        stats_data = {
            'current_reading': current_reading,
            'total_today': total_today,
            'average_hourly': average_hourly,
            'total_yesterday': total_yesterday,
            'change_percentage': change_percentage,
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
