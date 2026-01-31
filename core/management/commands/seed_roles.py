"""
Django management command to seed the roles table with predefined partner roles.
Matches the frontend roles defined in hydrosync-partner/lib/auth.ts
"""
import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Roles


class Command(BaseCommand):
    help = 'Seeds the roles table with predefined partner roles'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting roles seeding...'))

        roles_data = [
            {
                'name': 'admin',
                'description': 'System Administrator - Full system access and user management',
                'permission': {'level': 5},
                'is_active': True,
            },
            {
                'name': 'manager',
                'description': 'Operations Manager - Manage operations, reports, and team oversight',
                'permission': {'level': 4},
                'is_active': True,
            },
            {
                'name': 'technician',
                'description': 'Field Technician - Field operations and maintenance tasks',
                'permission': {'level': 3},
                'is_active': True,
            },
            {
                'name': 'operator',
                'description': 'System Operator - Monitor and control water systems',
                'permission': {'level': 3},
                'is_active': True,
            },
            {
                'name': 'customer_service',
                'description': 'Customer Service - Handle customer inquiries and support',
                'permission': {'level': 2},
                'is_active': True,
            },
            {
                'name': 'viewer',
                'description': 'Read-Only User - View-only access to basic information',
                'permission': {'level': 1},
                'is_active': True,
            },
        ]

        created_count = 0
        updated_count = 0
        now = timezone.now()

        for role_data in roles_data:
            # Check if role exists to get its created_at timestamp
            existing_role = Roles.objects.filter(name=role_data['name']).first()
            
            role, created = Roles.objects.update_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'permission': role_data['permission'],
                    'is_active': role_data['is_active'],
                    'created_at': existing_role.created_at if existing_role else now,
                    'updated_at': now,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created role: {role.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated role: {role.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Roles seeding complete!'))
        self.stdout.write(self.style.SUCCESS(f'   Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'   Updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'   Total: {len(roles_data)}'))
