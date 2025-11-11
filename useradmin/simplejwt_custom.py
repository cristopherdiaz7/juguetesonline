from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView


class SafeTokenRefreshSerializer(TokenRefreshSerializer):
    """Wrap TokenRefreshSerializer to return a proper AuthenticationFailed
    when the user referenced in the refresh token no longer exists.

    The upstream serializer can raise a DoesNotExist which bubbles as a
    500; catching it and raising AuthenticationFailed yields a 401 JSON
    response that the frontend can handle.
    """

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except ObjectDoesNotExist:
            # Map missing user to authentication failure (401) with a
            # clear message for the frontend.
            raise AuthenticationFailed("Usuario no encontrado")


class SafeTokenRefreshView(TokenRefreshView):
    serializer_class = SafeTokenRefreshSerializer
