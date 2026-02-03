"""
Django management command to seed the permissions table.
Creates fine-grained permissions for each role matching the frontend definition.
Based on hydrosync-partner/lib/auth.ts
"""
import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Roles, Permissions


class Command(BaseCommand):
    help = 'Seeds the permissions table with role-based permissions'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting permissions seeding...'))

        # Get all roles
        try:
            admin_role = Roles.objects.get(name='admin')
            manager_role = Roles.objects.get(name='manager')
            technician_role = Roles.objects.get(name='technician')
            operator_role = Roles.objects.get(name='operator')
            customer_service_role = Roles.objects.get(name='customer_service')
            viewer_role = Roles.objects.get(name='viewer')
        except Roles.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Roles not found! Please run seed_roles first'))
            return

        # Define permissions for each role
        permissions_map = {
            admin_role.id: [
                {'resource': '*', 'action': '*'},  # Admin has all permissions
            ],
            manager_role.id: [
                {'resource': 'dashboard', 'action': 'read'},
                {'resource': 'work_orders', 'action': 'write'},
                {'resource': 'reports', 'action': 'read'},
                {'resource': 'billing', 'action': 'write'},
                {'resource': 'analytics', 'action': 'read'},
                {'resource': 'users', 'action': 'read'},
                {'resource': 'customers', 'action': 'read'},
            ],
            technician_role.id: [
                {'resource': 'dashboard', 'action': 'read'},
                {'resource': 'work_orders', 'action': 'read'},
                {'resource': 'work_orders', 'action': 'update'},
                {'resource': 'meters', 'action': 'read'},
                {'resource': 'field', 'action': 'write'},
                {'resource': 'assets', 'action': 'read'},
            ],
            operator_role.id: [
                {'resource': 'dashboard', 'action': 'read'},
                {'resource': 'meters', 'action': 'read'},
                {'resource': 'quality', 'action': 'read'},
                {'resource': 'emergency', 'action': 'write'},
                {'resource': 'map', 'action': 'read'},
            ],
            customer_service_role.id: [
                {'resource': 'clients', 'action': 'read'},
                {'resource': 'billing', 'action': 'write'},
                {'resource': 'customer_portal', 'action': 'write'},
                {'resource': 'revenue', 'action': 'read'},
            ],
            viewer_role.id: [
                {'resource': 'dashboard', 'action': 'read'},
                {'resource': 'reports', 'action': 'read'},
            ],
        }

        created_count = 0
        now = timezone.now()

        # Clear existing permissions to avoid duplicates
        self.stdout.write(self.style.WARNING('Clearing existing permissions...'))
        Permissions.objects.all().delete()

        # Create permissions
        for role_id, permissions in permissions_map.items():
            role = Roles.objects.get(id=role_id)
            
            for perm_data in permissions:
                permission = Permissions.objects.create(
                    id=uuid.uuid4(),
                    role=role,
                    resource=perm_data['resource'],
                    action=perm_data['action'],
                    created_at=now,
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created: {role.name} → {perm_data["resource"]}:{perm_data["action"]}'
                    )
                )

        self.stdout.write(self.style.SUCCESS(f'\n✅ Permissions seeding complete!'))
        self.stdout.write(self.style.SUCCESS(f'   Total permissions created: {created_count}'))
