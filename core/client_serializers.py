from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import CustomerUsers

class ClientTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer for Client Users (CustomerUsers).
    Adds 'client' type claim to distinguish from staff users.
    """
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['type'] = 'client'
        token['name'] = user.name
        token['email'] = user.email
        token['customer_id'] = str(user.customer.id) if user.customer else None

        return token

class CustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUsers
        fields = [
            'id', 'email', 'name', 'phone', 
            'is_primary', 'is_active', 'last_login',
            'language_preference', 'theme_preference'
        ]
        read_only_fields = ['id', 'last_login']
