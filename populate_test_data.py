"""
Script to populate the database with test data for water consumption
Run with: python manage.py shell < populate_test_data.py
Or: python manage.py shell
Then: exec(open('populate_test_data.py').read())
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from core.models import Customers, Meters, MeterReadings, RegionalZones, BillingCycles
import random

print("🚀 Starting to populate test data...")

# Create a regional zone if it doesn't exist
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
print(f"✓ Regional Zone: {region.name} {'(created)' if created else '(existing)'}")

# Create a billing cycle if it doesn't exist
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
print(f"✓ Billing Cycle: {billing_cycle.name} {'(created)' if created else '(existing)'}")

# Create a test customer if it doesn't exist
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
print(f"✓ Customer: {customer.name} {'(created)' if created else '(existing)'}")

# Create a test meter if it doesn't exist
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
print(f"✓ Meter: {meter.meter_id} {'(created)' if created else '(existing)'}")

# Generate test readings for the last 24 hours
print("\n📊 Generating meter readings for the last 24 hours...")

now = timezone.now()
readings_created = 0

# Generate readings every 5 minutes for the last 24 hours
for i in range(288):  # 24 hours * 60 minutes / 5 minutes = 288 readings
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
    
    # Check if reading already exists for this time
    existing = MeterReadings.objects.filter(
        meter=meter,
        reading_date=reading_time
    ).exists()
    
    if not existing:
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

print(f"✓ Created {readings_created} new meter readings")

# Update meter's last reading
latest_reading = MeterReadings.objects.filter(meter=meter).order_by('-reading_date').first()
if latest_reading:
    meter.last_reading = latest_reading.reading_value
    meter.last_reading_date = latest_reading.reading_date
    meter.save()
    print(f"✓ Updated meter last reading: {meter.last_reading} L at {meter.last_reading_date}")

# Display summary
total_readings = MeterReadings.objects.filter(meter=meter).count()
total_consumption = MeterReadings.objects.filter(meter=meter).aggregate(
    total=models.Sum('reading_value')
)['total'] or Decimal('0.000')

print("\n" + "="*50)
print("📈 SUMMARY")
print("="*50)
print(f"Customer: {customer.name}")
print(f"Meter ID: {meter.meter_id}")
print(f"Total Readings: {total_readings}")
print(f"Total Consumption: {total_consumption} L")
print(f"Latest Reading: {meter.last_reading} L")
print(f"Status: {meter.status}")
print("="*50)
print("\n✅ Test data population completed!")
print("\n🔗 You can now test the API endpoints:")
print("   - http://localhost:8000/api/readings/latest/")
print("   - http://localhost:8000/api/readings/realtime/")
print("   - http://localhost:8000/api/dashboard/overview/")
print("   - http://localhost:8000/api/meters/")
