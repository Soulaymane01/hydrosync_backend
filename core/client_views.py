from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.hashers import check_password
from .models import CustomerUsers
from .client_serializers import ClientTokenObtainPairSerializer, CustomerUserSerializer

class ClientLoginView(TokenObtainPairView):
    """
    Client Login View.
    Authenticates user against CustomerUsers table and returns JWT tokens with 'client' type claim.
    """
    serializer_class = ClientTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Manually authentication check since we aren't using standard auth backend for this
            user = CustomerUsers.objects.get(email=email)
            if not check_password(password, user.password):
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_active:
                return Response({'error': 'Account is inactive'}, status=status.HTTP_403_FORBIDDEN)
            
            # Generate tokens using our custom serializer
            refresh = ClientTokenObtainPairSerializer.get_token(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': CustomerUserSerializer(user).data
            }, status=status.HTTP_200_OK)

        except CustomerUsers.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ClientLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            # If standard logout/blacklist is needed:
            # token = RefreshToken(refresh_token)
            # token.blacklist()
            return Response({"success": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ClientMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomerUserSerializer(request.user)
        return Response(serializer.data)
