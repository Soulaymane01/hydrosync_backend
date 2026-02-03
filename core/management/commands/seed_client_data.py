from django.core.management.base import BaseCommand
from core.models import RegionalZones, BillingCycles, Customers, CustomerUsers
from django.contrib.auth.hashers import make_password
import uuid

class Command(BaseCommand):
    help = 'Seeds initial client data (Regions, Billing Cycles, Demo Customer)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding client data...')

        # 1. Seed Regional Zones
        north_zone, created = RegionalZones.objects.get_or_create(
            name='North Region',
            defaults={
                'description': 'Northern operating zone targeting Tangier-Tetouan',
                'total_customers': 0,
                'total_meters': 0
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created North Region'))

        # 2. Seed Billing Cycles
        monthly_cycle, created = BillingCycles.objects.get_or_create(
            name='Standard Monthly',
            defaults={
                'frequency': 'monthly',
                'day_of_month': 1,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Standard Monthly Cycle'))

        # 3. Seed Demo Customer (Contract Owner)
        # Using a fixed ID/Name for easy retrieval during dev
        customer, created = Customers.objects.get_or_create(
            customer_id='CUST-001',
            defaults={
                'name': 'Hassan Amrani',
                'address': '123 Rue de la Liberté',
                'city': 'Tangier',
                'state': 'Tanger-Tetouan-Al Hoceima',
                'zip_code': '90000',
                'country': 'Morocco',
                'region': north_zone,
                'phone': '+212600000001',
                'email': 'hassan.amrani@example.com',
                'billing_cycle': monthly_cycle,
                'status': 'active',
                'balance': 0.00
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Customer: {customer.name}'))
        else:
            self.stdout.write(f'Customer {customer.name} already exists')

        # 4. Seed Customer User (Login Account)
        # Check if user exists by email
        user_email = 'client@hydrosync.com'
        if not CustomerUsers.objects.filter(email=user_email).exists():
            CustomerUsers.objects.create(
                customer=customer,
                email=user_email,
                password=make_password('password123'), # Hash the password!
                name='Hassan Amrani',
                phone='+212600000001',
                is_primary=True,
                is_active=True,
                notification_email=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created Customer User: {user_email} (password: password123)'))
        else:
            self.stdout.write(f'Customer User {user_email} already exists')
