from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from .models import Users, CustomerUsers
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.settings import api_settings

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        # Check for user type claim (default to 'staff' if missing for backward compatibility)
        user_type = validated_token.get('type', 'staff')

        try:
            if user_type == 'client':
                user = CustomerUsers.objects.get(**{api_settings.USER_ID_FIELD: user_id})
                if not user.is_active: # CustomerUsers has boolean is_active
                    raise AuthenticationFailed(_("User is inactive"), code="user_inactive")
            else:
                # Default Staff User Logic
                user = Users.objects.get(**{api_settings.USER_ID_FIELD: user_id})
                if not user.status == 'active': # Users has string status
                     raise AuthenticationFailed(_("User is inactive"), code="user_inactive")

        except (Users.DoesNotExist, CustomerUsers.DoesNotExist):
            raise AuthenticationFailed(_("User not found"), code="user_not_found")

        return user
