# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import uuid
from django.db import models
from django.contrib.auth.models import User



class Assets(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_id = models.CharField(unique=True, max_length=100)
    type = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)
    region = models.ForeignKey('RegionalZones', models.DO_NOTHING, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, default='active')
    purchase_date = models.DateField(blank=True, null=True)
    warranty_end = models.DateField(blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    next_maintenance_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'assets'
        db_table_comment = 'Infrastructure assets - pump, tank, pipe, valve, treatment_plant'


class AuditLogs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(blank=True, null=True)
    user_type = models.CharField(max_length=50, blank=True, null=True)
    user_email = models.CharField(max_length=255, blank=True, null=True)
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=255, blank=True, null=True)
    changes = models.JSONField(blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'audit_logs'
        db_table_comment = 'Audit trail - user_type: partner_user, customer_user, system'


class BillingCycles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)
    frequency = models.CharField(max_length=50)
    day_of_month = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True, default=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'billing_cycles'
        db_table_comment = 'Billing schedules - frequency: monthly, quarterly, annually'


class CustomerUsers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('Customers', models.DO_NOTHING)
    email = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(blank=True, null=True, default=False)
    is_active = models.BooleanField(blank=True, null=True, default=True)
    last_login = models.DateTimeField(blank=True, null=True)
    two_factor_enabled = models.BooleanField(blank=True, null=True, default=False)
    two_factor_method = models.CharField(max_length=50, blank=True, null=True)
    notification_email = models.BooleanField(blank=True, null=True, default=True)
    notification_sms = models.BooleanField(blank=True, null=True, default=False)
    newsletter_opted_in = models.BooleanField(blank=True, null=True, default=True)
    language_preference = models.CharField(max_length=10, blank=True, null=True, default='en')
    theme_preference = models.CharField(max_length=50, blank=True, null=True, default='system')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
    
    # is_active field already exists as BooleanField, but we can add property or just use the field.
    # The models.BooleanField(db_column='is_active') is already there. 
    # But for consistency with User model override, let's just rely on the field attribute.

    def get_username(self):
        return self.email

    class Meta:
        managed = True
        db_table = 'customer_users'
        db_table_comment = 'Portal login accounts - Multiple users per customer account (family members, staff)'


class Customers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.CharField(unique=True, max_length=50)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True, default='Morocco')
    region = models.ForeignKey('RegionalZones', models.DO_NOTHING, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    account_type = models.CharField(max_length=50, blank=True, null=True)
    billing_cycle = models.ForeignKey(BillingCycles, models.DO_NOTHING, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, default='active')
    balance = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0.00)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'customers'
        db_table_comment = 'Billing accounts - Can have multiple portal users and meters'


class EnvironmentalData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(max_length=50, blank=True, null=True)
    target_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, default='normal')
    region = models.ForeignKey('RegionalZones', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'environmental_data'
        db_table_comment = 'Environmental metrics - water_loss, carbon_emissions, sustainability_goal'


class Invoices(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_id = models.CharField(unique=True, max_length=50)
    customer = models.ForeignKey(Customers, models.DO_NOTHING)
    meter = models.ForeignKey('Meters', models.DO_NOTHING, blank=True, null=True)
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    usage_amount = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True)
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0.00)
    late_fees = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0.00)
    status = models.CharField(max_length=50, blank=True, null=True, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'invoices'
        db_table_comment = 'Bills generated for water usage - status: pending, paid, overdue, cancelled, partial'


class LeakDetectionEvents(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meter = models.ForeignKey('Meters', models.DO_NOTHING)
    anomaly_level = models.CharField(max_length=50)
    detected_value = models.DecimalField(max_digits=8, decimal_places=4)
    normal_range = models.DecimalField(max_digits=8, decimal_places=4)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, default='active')
    acknowledged_by = models.ForeignKey('Users', models.DO_NOTHING, db_column='acknowledged_by', blank=True, null=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'leak_detection_events'
        db_table_comment = 'Water leak detection - anomaly_level: low, medium, high, critical'


class Maintenance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    maintenance_id = models.CharField(unique=True, max_length=50)
    asset = models.ForeignKey(Assets, models.DO_NOTHING)
    type = models.CharField(max_length=50)
    scheduled_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    performed_by = models.ForeignKey('Users', models.DO_NOTHING, db_column='performed_by', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, default='scheduled')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'maintenance'
        db_table_comment = 'Asset maintenance records - preventive, corrective, emergency'


class MeterReadings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meter = models.ForeignKey('Meters', models.DO_NOTHING)
    reading_value = models.DecimalField(max_digits=12, decimal_places=3)
    unit = models.CharField(max_length=20, blank=True, null=True, default='m3')
    reading_date = models.DateTimeField()
    reading_type = models.CharField(max_length=50, blank=True, null=True, default='automatic')
    anomaly_detected = models.BooleanField(blank=True, null=True, default=False)
    usage_status = models.CharField(max_length=50, blank=True, null=True, default='normal')
    quality_status = models.CharField(max_length=50, blank=True, null=True, default='good')
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'meter_readings'
        db_table_comment = 'Individual water usage readings - millions of records'


class Meters(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meter_id = models.CharField(unique=True, max_length=100)
    customer = models.ForeignKey(Customers, models.DO_NOTHING)
    type = models.CharField(max_length=50)
    model = models.CharField(max_length=100, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    install_date = models.DateField()
    last_reading = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True)
    last_reading_date = models.DateTimeField(blank=True, null=True)
    error_status = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, default='active')
    firmware_version = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'meters'
        db_table_comment = 'Water meters - smart, analog, hybrid types'


class Notifications(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification_id = models.CharField(unique=True, max_length=50)
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, blank=True, null=True)
    priority = models.CharField(max_length=50, blank=True, null=True, default='medium')
    recipient_type = models.CharField(max_length=50, blank=True, null=True)
    recipient_id = models.UUIDField(blank=True, null=True)
    delivery_method = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, default='pending')
    action_url = models.CharField(max_length=500, blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'notifications'
        db_table_comment = 'Unified notifications - recipient_type: partner_user, customer_user, role, region, all'


class PaymentMethods(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_user = models.ForeignKey(CustomerUsers, models.DO_NOTHING)
    type = models.CharField(max_length=50)
    card_number_encrypted = models.CharField(max_length=255, blank=True, null=True)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    holder_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(blank=True, null=True, default=False)
    is_active = models.BooleanField(blank=True, null=True, default=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'payment_methods'
        db_table_comment = 'Saved payment methods - credit_card, debit_card, bank_transfer, e_wallet'


class Payments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_id = models.CharField(unique=True, max_length=50)
    invoice = models.ForeignKey(Invoices, models.DO_NOTHING)
    customer_user = models.ForeignKey(CustomerUsers, models.DO_NOTHING, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethods, models.DO_NOTHING, blank=True, null=True)
    payment_method_name = models.CharField(max_length=100, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, default='completed')
    processed_by = models.ForeignKey('Users', models.DO_NOTHING, db_column='processed_by', blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'payments'
        db_table_comment = 'Payment transactions - Multiple payments can be made for one invoice'


class Permissions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey('Roles', models.DO_NOTHING)
    resource = models.CharField(max_length=100)
    action = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'permissions'
        unique_together = (('role', 'resource', 'action'),)
        db_table_comment = 'Fine-grained permissions for roles'


class QualityData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meter = models.ForeignKey(Meters, models.DO_NOTHING)
    ph_level = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    turbidity = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    chlorine = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    hardness = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    timestamp = models.DateTimeField()
    status = models.CharField(max_length=50, blank=True, null=True, default='good')
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'quality_data'
        db_table_comment = 'Water quality measurements - pH, turbidity (NTU), chlorine (mg/L), etc.'


class RegionalZones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    total_customers = models.IntegerField(blank=True, null=True, default=0)
    total_meters = models.IntegerField(blank=True, null=True, default=0)
    average_usage = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'regional_zones'
        db_table_comment = 'Geographic service regions'


class Roles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    permission = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'roles'
        db_table_comment = 'User roles: admin, operator, technician, customer_service, viewer, manager'


class SupportTickets(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_id = models.CharField(unique=True, max_length=50)
    customer_user = models.ForeignKey(CustomerUsers, models.DO_NOTHING)
    customer = models.ForeignKey(Customers, models.DO_NOTHING)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=50, blank=True, null=True, default='medium')
    status = models.CharField(max_length=50, blank=True, null=True, default='open')
    category = models.CharField(max_length=100, blank=True, null=True)
    assigned_to = models.ForeignKey('Users', models.DO_NOTHING, db_column='assigned_to', blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'support_tickets'
        db_table_comment = 'Customer support tickets - category: billing, technical, service_request, complaint'


class UsageGoals(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meter = models.ForeignKey(Meters, models.DO_NOTHING)
    target_usage = models.DecimalField(max_digits=12, decimal_places=3)
    month = models.IntegerField()
    year = models.IntegerField()
    status = models.CharField(max_length=50, blank=True, null=True, default='active')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usage_goals'
        unique_together = (('meter', 'month', 'year'),)
        db_table_comment = 'Customer-set monthly water usage targets'


class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    firstname = models.CharField(db_column='firstName', max_length=100)  # Field name made lowercase.
    lastname = models.CharField(db_column='lastName', max_length=100)  # Field name made lowercase.
    role = models.ForeignKey(Roles, models.DO_NOTHING)
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, default='active')
    avatar_url = models.TextField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.status == 'active'

    def get_username(self):
        return self.email

    class Meta:
        managed = True
        db_table = 'users'
        db_table_comment = 'Partner users - Staff members (admin, operator, technician, etc.)'


class WorkOrders(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order_id = models.CharField(unique=True, max_length=50)
    customer = models.ForeignKey(Customers, models.DO_NOTHING)
    meter = models.ForeignKey(Meters, models.DO_NOTHING, blank=True, null=True)
    assigned_to = models.ForeignKey(Users, models.DO_NOTHING, db_column='assigned_to', blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=50, blank=True, null=True, default='medium')
    status = models.CharField(max_length=50, blank=True, null=True, default='open')
    scheduled_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'work_orders'
        db_table_comment = 'Field service requests - priority: low, medium, high, critical'