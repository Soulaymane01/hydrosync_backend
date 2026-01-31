"""
Serializers for authentication and user management API endpoints
"""
from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from core.models import Users, Roles, Permissions


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for permission objects"""
    
    class Meta:
        model = Permissions
        fields = ['id', 'resource', 'action']


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for role objects with their permissions"""
    permissions = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    
    class Meta:
        model = Roles
        fields = ['id', 'name', 'description', 'level', 'is_active', 'permissions']
    
    def get_permissions(self, obj):
        """Get all permissions for this role"""
        permissions = Permissions.objects.filter(role=obj)
        return PermissionSerializer(permissions, many=True).data
    
    def get_level(self, obj):
        """Get permission level from JSON field"""
        if obj.permission and 'level' in obj.permission:
            return obj.permission['level']
        return 0


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user objects"""
    role_details = RoleSerializer(source='role', read_only=True)
    permissions = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = Users
        fields = [
            'id', 'email', 'firstname', 'lastname', 'name',
            'role', 'role_details', 'permissions', 'department', 
            'phone', 'status', 'avatar_url', 'last_login',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def get_name(self, obj):
        """Get full name"""
        return f"{obj.firstname} {obj.lastname}"
    
    def get_permissions(self, obj):
        """Get all permissions for the user's role"""
        permissions = Permissions.objects.filter(role=obj.role)
        return PermissionSerializer(permissions, many=True).data


class LoginSerializer(serializers.Serializer):
    """Serializer for login requests"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        """Validate email and password"""
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise serializers.ValidationError('Email and password are required')
        
        try:
            user = Users.objects.select_related('role').get(email=email)
        except Users.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password')
        
        # Check password
        if not check_password(password, user.password):
            raise serializers.ValidationError('Invalid email or password')
        
        # Check if user is active
        if user.status != 'active':
            raise serializers.ValidationError('User account is inactive')
        
        # Check if deleted
        if user.deleted_at is not None:
            raise serializers.ValidationError('User account has been deleted')
        
        data['user'] = user
        return data


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    
    class Meta:
        model = Users
        fields = [
            'email', 'password', 'firstname', 'lastname',
            'role', 'department', 'phone', 'status'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        """Create a new user with hashed password"""
        from django.contrib.auth.hashers import make_password
        from django.utils import timezone
        
        validated_data['password'] = make_password(validated_data['password'])
        validated_data['created_at'] = timezone.now()
        validated_data['updated_at'] = timezone.now()
        
        user = Users.objects.create(**validated_data)
        return user
