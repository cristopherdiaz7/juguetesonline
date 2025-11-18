from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.db import transaction

from .models import Usuario as UserAdminUsuario
from ventas.models import Usuario as VentasUsuario
import hashlib


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

        logger.warning('LegacyVentasBackend: useradmin lookup for username=%s found=%s', username, bool(user))

        # Second attempt: look up legacy ventas.Usuario by nombre or correo
        legacy_qs = VentasUsuario.objects.filter(nombre__iexact=username) | VentasUsuario.objects.filter(correo__iexact=username)
        legacy = legacy_qs.first()
        logger.warning('LegacyVentasBackend: legacy lookup for identifier=%s found=%s', username, bool(legacy))
        if not legacy:
            return None

        legacy_hash = getattr(legacy, 'contraseña', '') or ''
        logger.debug('LegacyVentasBackend: legacy.hash present=%s', bool(legacy_hash))
        if not legacy_hash:
            return None

        # Verify provided password against the stored legacy hash
        try:
            # First try Django's check_password (works if legacy_hash already uses a
            # Django-compatible format like 'pbkdf2_sha256$...').
            if check_password(password, legacy_hash):
                with transaction.atomic():
                    u, created = UserAdminUsuario.objects.get_or_create(username=legacy.nombre)
                    u.email = legacy.correo or u.email or f"{legacy.nombre}@no-email.local"
                    u.tipo = getattr(legacy, 'tipo', getattr(u, 'tipo', 'comprador'))
                    u.direccion = getattr(legacy, 'direccion', getattr(u, 'direccion', ''))
                    u.is_active = True
                    # If the legacy hash is already in Django format (contains '$'),
                    # preserve it so Django can validate it in the future.
                    if '$' in legacy_hash:
                        u.password = legacy_hash
                    else:
                        # Legacy hash is not Django format — migrate the user to a
                        # Django hash by setting the password to the plain password
                        # provided (we already verified it matches the legacy scheme).
                        u.set_password(password)
                    if getattr(legacy, 'tipo', '') == 'vendedor':
                        u.is_staff = True
                    u.save()
                    logger.warning('LegacyVentasBackend: imported/updated useradmin username=%s id=%s created=%s', u.username, u.id, created)
                return u

            # If Django's check failed, try common legacy raw-hash formats (MD5, SHA1)
            # which may be stored as hex digests without algorithm prefix.
            legacy_hash_lower = legacy_hash.lower()
            if len(legacy_hash_lower) == 32 and all(c in '0123456789abcdef' for c in legacy_hash_lower):
                # MD5
                md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
                if md5 == legacy_hash_lower:
                    with transaction.atomic():
                        u, created = UserAdminUsuario.objects.get_or_create(username=legacy.nombre)
                        u.email = legacy.correo or u.email or f"{legacy.nombre}@no-email.local"
                        u.tipo = getattr(legacy, 'tipo', getattr(u, 'tipo', 'comprador'))
                        u.direccion = getattr(legacy, 'direccion', getattr(u, 'direccion', ''))
                        u.is_active = True
                        # Migrate to Django hash
                        u.set_password(password)
                        if getattr(legacy, 'tipo', '') == 'vendedor':
                            u.is_staff = True
                        u.save()
                        logger.warning('LegacyVentasBackend: migrated MD5 legacy user %s -> id=%s created=%s', u.username, u.id, created)
                    return u

            if len(legacy_hash_lower) == 40 and all(c in '0123456789abcdef' for c in legacy_hash_lower):
                # SHA1
                sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest()
                if sha1 == legacy_hash_lower:
                    with transaction.atomic():
                        u, created = UserAdminUsuario.objects.get_or_create(username=legacy.nombre)
                        u.email = legacy.correo or u.email or f"{legacy.nombre}@no-email.local"
                        u.tipo = getattr(legacy, 'tipo', getattr(u, 'tipo', 'comprador'))
                        u.direccion = getattr(legacy, 'direccion', getattr(u, 'direccion', ''))
                        u.is_active = True
                        u.set_password(password)
                        if getattr(legacy, 'tipo', '') == 'vendedor':
                            u.is_staff = True
                        u.save()
                        logger.warning('LegacyVentasBackend: migrated SHA1 legacy user %s -> id=%s created=%s', u.username, u.id, created)
                    return u

            logger.warning('LegacyVentasBackend: password did not match legacy hash for %s', username)
            return None
        except Exception as e:
            logger.exception('LegacyVentasBackend: exception during legacy auth for %s: %s', username, e)
            return None

        return None
