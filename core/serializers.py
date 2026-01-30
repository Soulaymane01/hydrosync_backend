# serializers.py
from rest_framework import serializers
from .models import MeterReadings, Meters, Customers
from django.db.models import Sum, Avg, Max
from datetime import datetime, timedelta


class MeterSerializer(serializers.ModelSerializer):
    """Serializer for Meter information"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = Meters
        fields = [
            'id', 'meter_id', 'customer', 'customer_name', 'type', 
            'model', 'manufacturer', 'serial_number', 'location',
            'install_date', 'last_reading', 'last_reading_date',
            'status', 'firmware_version'
        ]


class MeterReadingSerializer(serializers.ModelSerializer):
    """Serializer for individual meter readings"""
    meter_id = serializers.CharField(source='meter.meter_id', read_only=True)
    meter_location = serializers.CharField(source='meter.location', read_only=True)
    
    class Meta:
        model = MeterReadings
        fields = [
            'id', 'meter', 'meter_id', 'meter_location',
            'reading_value', 'unit', 'reading_date', 'reading_type',
            'anomaly_detected', 'usage_status', 'quality_status',
            'created_at'
        ]


class RealtimeReadingSerializer(serializers.ModelSerializer):
    """Optimized serializer for real-time data display"""
    meter_id = serializers.CharField(source='meter.meter_id', read_only=True)
    
    class Meta:
        model = MeterReadings
        fields = ['id', 'meter_id', 'reading_value', 'unit', 'reading_date', 'usage_status']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    current_reading = serializers.DecimalField(max_digits=12, decimal_places=3)
    total_today = serializers.DecimalField(max_digits=12, decimal_places=3)
    average_hourly = serializers.DecimalField(max_digits=12, decimal_places=3)
    total_yesterday = serializers.DecimalField(max_digits=12, decimal_places=3)
    change_percentage = serializers.DecimalField(max_digits=6, decimal_places=2)
    comparison_reliable = serializers.BooleanField()
    active_meters = serializers.IntegerField()
    total_readings_today = serializers.IntegerField()
