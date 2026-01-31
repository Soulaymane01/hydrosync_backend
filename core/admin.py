from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('email', 'firstname', 'lastname', 'role', 'status', 'created_at')
    search_fields = ('email', 'firstname', 'lastname')
    list_filter = ('role', 'status', 'department')
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        """Hash password when saving from admin"""
        from django.contrib.auth.hashers import make_password
        
        # If creating new user or password has changed
        if not change or 'password' in form.changed_data:
            obj.password = make_password(obj.password)
            
        super().save_model(request, obj, form, change)

@admin.register(Assets)
class AssetsAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'type', 'status', 'location', 'region')
    search_fields = ('asset_id', 'serial_number')
    list_filter = ('type', 'status', 'region')



