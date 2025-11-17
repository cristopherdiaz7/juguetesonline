from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


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


class ExtendedTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Accept either `username` or `email` in the token request body.

    If `email` is provided we look up the corresponding username and
    let the usual authentication flow proceed. This makes it easier for
    the frontend to send an `email` field while keeping the backend
    authentication unchanged.
    """

    def validate(self, attrs):
        # If client supplied email instead of username, try to map it.
        username = attrs.get('username')
        if not username and 'email' in attrs:
            email = attrs.get('email')
            try:
                from .models import Usuario as UsuarioModel
                u = UsuarioModel.objects.filter(email__iexact=email).first()
                if u:
                    attrs['username'] = u.username
            except Exception:
                # If something goes wrong, fall back and let authentication fail normally.
                pass

        return super().validate(attrs)


class ExtendedTokenObtainPairView(TokenObtainPairView):
    serializer_class = ExtendedTokenObtainPairSerializer
