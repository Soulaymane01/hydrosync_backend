"""
API views for authentication and user management
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from core.models import Users
from core.serializers import (
    LoginSerializer, 
    UserSerializer, 
    UserCreateSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login endpoint - Returns JWT tokens and user data
    POST /api/auth/login
    Body: {"email": "user@example.com", "password": "password"}
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'success': False, 'message': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = serializer.validated_data['user']
    
    # Update last login
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    # Serialize user data
    user_serializer = UserSerializer(user)
    user_data = user_serializer.data
    
    # Add role information in frontend-compatible format
    user_data['role'] = {
        'id': user.role.name,  # Use role name as id for frontend compatibility
        'name': get_role_display_name(user.role.name),
        'level': user.role.permission.get('level', 0) if user.role.permission else 0,
        'description': user.role.description,
    }
    
    # Format permissions for frontend
    user_data['permissions'] = [
        {
            'id': f"{perm['resource']}_{perm['action']}",
            'name': f"{perm['resource'].title()} {perm['action'].title()}",
            'resource': perm['resource'],
            'action': perm['action'],
            'description': f"{perm['action'].title()} access to {perm['resource']}"
        }
        for perm in user_data['permissions']
    ]
    
    return Response({
        'success': True,
        'token': access_token,
        'refresh': refresh_token,
        'user': user_data,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout endpoint - Blacklists the refresh token
    POST /api/auth/logout
    Headers: Authorization: Bearer <token>
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Get current user endpoint
    GET /api/auth/me
    Headers: Authorization: Bearer <token>
    """
    user = request.user
    
    try:
        # Get the Users object (not Django auth_user)
        partner_user = Users.objects.select_related('role').get(email=user.email)
        serializer = UserSerializer(partner_user)
        user_data = serializer.data
        
        # Format for frontend compatibility
        user_data['role'] = {
            'id': partner_user.role.name,
            'name': get_role_display_name(partner_user.role.name),
            'level': partner_user.role.permission.get('level', 0) if partner_user.role.permission else 0,
            'description': partner_user.role.description,
        }
        
        # Format permissions
        user_data['permissions'] = [
            {
                'id': f"{perm['resource']}_{perm['action']}",
                'name': f"{perm['resource'].title()} {perm['action'].title()}",
                'resource': perm['resource'],
                'action': perm['action'],
                'description': f"{perm['action'].title()} access to {perm['resource']}"
            }
            for perm in user_data['permissions']
        ]
        
        return Response({
            'success': True,
            'user': user_data
        }, status=status.HTTP_200_OK)
    except Users.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


class UserListCreateView(generics.ListCreateAPIView):
    """
    GET /api/users - List all users
    POST /api/users - Create new user
    """
    queryset = Users.objects.filter(deleted_at__isnull=True).select_related('role')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response({
            'success': True,
            'users': serializer.data
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            return Response({
                'success': True,
                'message': 'User created successfully',
                'user': user_data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/users/:id - Get user details
    PUT /api/users/:id - Update user
    DELETE /api/users/:id - Delete user (soft delete)
    """
    queryset = Users.objects.filter(deleted_at__isnull=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete user"""
        user = self.get_object()
        user.deleted_at = timezone.now()
        user.status = 'inactive'
        user.save(update_fields=['deleted_at', 'status', 'updated_at'])
        
        return Response({
            'success': True,
            'message': 'User deleted successfully'
        }, status=status.HTTP_200_OK)


def get_role_display_name(role_name):
    """Convert role name to display name"""
    role_names = {
        'admin': 'System Administrator',
        'manager': 'Operations Manager',
        'technician': 'Field Technician',
        'operator': 'System Operator',
        'customer_service': 'Customer Service',
        'viewer': 'Read-Only User',
    }
    return role_names.get(role_name, role_name.replace('_', ' ').title())
