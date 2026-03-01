"""
Utility script to reset and repopulate test data for HydroSync
This script safely clears all meter readings and regenerates fresh test data.

Usage:
    python manage.py shell < reset_test_data.py

Or in Django shell:
    python manage.py shell
    >>> exec(open('reset_test_data.py').read())
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from core.models import Customers, Meters, MeterReadings, RegionalZones, BillingCycles
import random

print("=" * 60)
print("HYDROSYNC TEST DATA RESET UTILITY")
print("=" * 60)

# Step 1: Display current data statistics
print("\nCurrent database statistics:")
total_readings = MeterReadings.objects.count()
total_meters = Meters.objects.count()
total_customers = Customers.objects.count()

print(f"   Customers: {total_customers}")
print(f"   Meters: {total_meters}")
print(f"   Readings: {total_readings}")

if total_readings > 0:
    total_consumption = MeterReadings.objects.aggregate(
        total=Sum('reading_value')
    )['total'] or Decimal('0.000')
    print(f"   Total consumption: {total_consumption} L")

# Step 2: Confirm deletion
print("\nWARNING: This will DELETE all meter readings!")
print("   (Customers and Meters will be preserved)")

# Delete all meter readings
print("\nDeleting all meter readings...")
deleted_count, _ = MeterReadings.objects.all().delete()
print(f"Deleted {deleted_count} readings")

# Step 3: Regenerate test data
print("\n" + "=" * 60)
print("REGENERATING TEST DATA")
print("=" * 60)

# Create or get regional zone
region, created = RegionalZones.objects.get_or_create(
    name="Zone Test",
    defaults={
        'id': uuid.uuid4(),
        'description': 'Zone de test pour HydroSync',
        'total_customers': 0,
        'total_meters': 0,
        'average_usage': Decimal('0.000'),
        'created_at': timezone.now(),
        'updated_at': timezone.now()
    }
)
print(f"Regional Zone: {region.name} {'(created)' if created else '(existing)'}")

# Create or get billing cycle
billing_cycle, created = BillingCycles.objects.get_or_create(
    name="Monthly Test",
    defaults={
        'id': uuid.uuid4(),
        'frequency': 'monthly',
        'day_of_month': 1,
        'is_active': True,
        'created_at': timezone.now(),
        'updated_at': timezone.now()
    }
)
print(f"Billing Cycle: {billing_cycle.name} {'(created)' if created else '(existing)'}")

# Create or get test customer
customer, created = Customers.objects.get_or_create(
    customer_id="CUST-TEST-001",
    defaults={
        'id': uuid.uuid4(),
        'name': 'Client Test HydroSync',
        'address': '123 Rue de Test, Tunis',
        'city': 'Tunis',
        'state': 'Tunis',
        'zip_code': '1000',
        'country': 'Tunisia',
        'region': region,
        'phone': '+216 12 345 678',
        'email': 'test@hydrosync.tn',
        'contact_person': 'Ahmed Test',
        'account_type': 'residential',
        'billing_cycle': billing_cycle,
        'status': 'active',
        'balance': Decimal('0.00'),
        'created_at': timezone.now(),
        'updated_at': timezone.now()
    }
)
print(f"Customer: {customer.name} {'(created)' if created else '(existing)'}")

# Create or get test meter
meter, created = Meters.objects.get_or_create(
    meter_id="METER-ESP32-001",
    defaults={
        'id': uuid.uuid4(),
        'customer': customer,
        'type': 'smart',
        'model': 'ESP32-FlowMeter-v1',
        'manufacturer': 'HydroSync',
        'serial_number': 'ESP32-SN-001',
        'location': 'Entrée principale',
        'install_date': timezone.now().date(),
        'last_reading': Decimal('0.000'),
        'last_reading_date': timezone.now(),
        'error_status': 'none',
        'status': 'active',
        'firmware_version': '1.0.0',
        'created_at': timezone.now(),
        'updated_at': timezone.now()
    }
)
print(f"Meter: {meter.meter_id} {'(created)' if created else '(existing)'}")

# Generate test readings for the last 48 hours
print("\nGenerating meter readings for the last 48 hours...")

now = timezone.now()
readings_created = 0

# Generate readings every 5 minutes for the last 48 hours
for i in range(576):  # 48 hours * 60 minutes / 5 minutes = 576 readings
    reading_time = now - timedelta(minutes=5 * i)
    
    # Simulate realistic water consumption pattern
    hour = reading_time.hour
    
    # Higher consumption during morning (6-9) and evening (18-22)
    if 6 <= hour <= 9 or 18 <= hour <= 22:
        base_flow = random.uniform(2.0, 5.0)  # Liters
    elif 22 <= hour or hour <= 6:
        base_flow = random.uniform(0.1, 0.5)  # Night time, minimal usage
    else:
        base_flow = random.uniform(0.5, 2.0)  # Normal usage
    
    # Add some random variation
    reading_value = Decimal(str(round(base_flow + random.uniform(-0.2, 0.2), 3)))
    
    # Ensure positive values
    if reading_value < 0:
        reading_value = Decimal('0.100')
    
    # Determine usage status based on flow rate
    if reading_value > 4.0:
        usage_status = 'high'
    elif reading_value > 2.0:
        usage_status = 'normal'
    else:
        usage_status = 'low'
    
    # Create reading
    reading = MeterReadings.objects.create(
        id=uuid.uuid4(),
        meter=meter,
        reading_value=reading_value,
        unit='L',
        reading_date=reading_time,
        reading_type='automatic',
        anomaly_detected=False,
        usage_status=usage_status,
        quality_status='good',
        created_at=reading_time
    )
    readings_created += 1

print(f"Created {readings_created} new meter readings")

# Update meter's last reading
latest_reading = MeterReadings.objects.filter(meter=meter).order_by('-reading_date').first()
if latest_reading:
    meter.last_reading = latest_reading.reading_value
    meter.last_reading_date = latest_reading.reading_date
    meter.save()
    print(f"Updated meter last reading: {meter.last_reading} L at {meter.last_reading_date}")

# Display summary with today/yesterday breakdown
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
yesterday_start = today_start - timedelta(days=1)

today_stats = MeterReadings.objects.filter(
    meter=meter,
    reading_date__gte=today_start
).aggregate(total=Sum('reading_value'))

yesterday_stats = MeterReadings.objects.filter(
    meter=meter,
    reading_date__gte=yesterday_start,
    reading_date__lt=today_start
).aggregate(total=Sum('reading_value'))

total_consumption = MeterReadings.objects.filter(meter=meter).aggregate(
    total=Sum('reading_value')
)['total'] or Decimal('0.000')

print(f"Customer: {customer.name}")
print(f"Meter ID: {meter.meter_id}")
print(f"Total Readings: {readings_created}")
print(f"Total Consumption (48h): {total_consumption} L")
print(f"\nToday's consumption: {today_stats['total'] or Decimal('0.000')} L")
print(f"Yesterday's consumption: {yesterday_stats['total'] or Decimal('0.000')} L")
print(f"Latest Reading: {meter.last_reading} L")
print(f"Status: {meter.status}")
print("=" * 60)

print("\nTest data reset and regeneration completed!")
print("\nYou can now test the API endpoints:")
print("   - http://localhost:8000/api/readings/latest/")
print("   - http://localhost:8000/api/readings/realtime/")
print("   - http://localhost:8000/api/dashboard/overview/")
print("   - http://localhost:8000/api/meters/")
print("\nTip: Run this script anytime you need fresh, balanced test data!")
