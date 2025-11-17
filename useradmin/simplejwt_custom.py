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
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import logging


class DirectTokenObtainView(APIView):
    """Direct token endpoint: accepts `username` or `email` and `password`.

    This view performs an explicit `authenticate()` call and returns
    `access`/`refresh` tokens using `RefreshToken.for_user` on success.
    It's more explicit and logs detailed info to help debug 401s in prod.
    """

    def post(self, request, *args, **kwargs):
        logger = logging.getLogger('useradmin.token')
        data = request.data or {}
        username = data.get('username')
        password = data.get('password')
        # If email provided, try to map to username
        if not username and data.get('email'):
            try:
                from .models import Usuario as UsuarioModel
                u = UsuarioModel.objects.filter(email__iexact=data.get('email')).first()
                if u:
                    username = u.username
            except Exception:
                pass

        logger.info('DirectTokenObtain: auth attempt username=%s present_password=%s', username, bool(password))

        if not username or not password:
            return Response({'detail': 'username/email and password required'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        if user is None:
            logger.warning('DirectTokenObtain: authenticate failed for username=%s', username)
            return Response({'detail': 'No active account found with the given credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Build tokens
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
