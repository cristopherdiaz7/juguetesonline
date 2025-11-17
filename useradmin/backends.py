from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.db import transaction

from .models import Usuario as UserAdminUsuario
from ventas.models import Usuario as VentasUsuario


class LegacyVentasBackend(ModelBackend):
    """
    Authentication backend that first tries the default ModelBackend (useradmin.Usuario).
    If no user is found or password fails, it checks the legacy ventas.Usuario table
    (matching by username or email). If a match is found and the legacy hash verifies,
    it will create or update the corresponding `useradmin.Usuario` record preserving
    the legacy hash so subsequent logins use the Django auth table.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # First attempt: use the default ModelBackend logic for useradmin.Usuario
        user = None
        try:
            user = UserAdminUsuario.objects.get(username=username)
            if user.check_password(password):
                return user
        except UserAdminUsuario.DoesNotExist:
            user = None
        import logging
        logger = logging.getLogger('useradmin.legacy')

        logger.info('LegacyVentasBackend: useradmin lookup for username=%s found=%s', username, bool(user))

        # Second attempt: look up legacy ventas.Usuario by nombre or correo
        legacy_qs = VentasUsuario.objects.filter(nombre__iexact=username) | VentasUsuario.objects.filter(correo__iexact=username)
        legacy = legacy_qs.first()
        logger.info('LegacyVentasBackend: legacy lookup for identifier=%s found=%s', username, bool(legacy))
        if not legacy:
            return None

        legacy_hash = getattr(legacy, 'contraseña', '') or ''
        logger.debug('LegacyVentasBackend: legacy.hash present=%s', bool(legacy_hash))
        if not legacy_hash:
            return None

        # Verify provided password against the stored legacy hash
        try:
            if check_password(password, legacy_hash):
                # Password matches legacy record. Create or update useradmin.Usuario.
                with transaction.atomic():
                    u, created = UserAdminUsuario.objects.get_or_create(username=legacy.nombre)
                    # Map fields
                    u.email = legacy.correo or u.email or f"{legacy.nombre}@no-email.local"
                    u.tipo = getattr(legacy, 'tipo', getattr(u, 'tipo', 'comprador'))
                    u.direccion = getattr(legacy, 'direccion', getattr(u, 'direccion', ''))
                    u.is_active = True
                    # Preserve the legacy hash in the Django password field
                    u.password = legacy_hash
                    # If legacy user is a vendedor, give staff flag
                    if getattr(legacy, 'tipo', '') == 'vendedor':
                        u.is_staff = True
                    u.save()
                    logger.info('LegacyVentasBackend: imported/updated useradmin username=%s id=%s created=%s', u.username, u.id, created)
                return u
            else:
                logger.warning('LegacyVentasBackend: password did not match legacy hash for %s', username)
                return None
        except Exception:
            logger.exception('LegacyVentasBackend: exception during legacy auth for %s: %s', username, e)
            return None

        return None
