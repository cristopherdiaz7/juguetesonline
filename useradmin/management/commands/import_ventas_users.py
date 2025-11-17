from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.hashers import identify_hasher

from ventas.models import Usuario as VentasUsuario
from useradmin.models import Usuario as UserAdminUsuario


class Command(BaseCommand):
    help = 'Import usuarios from ventas.Usuario into useradmin.Usuario preserving password hash.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Do not write changes; just report')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of rows processed (0 = no limit)')
        parser.add_argument('--username', type=str, help='Import only this username')
        parser.add_argument('--only-missing', action='store_true', default=True, help='Only import users missing in useradmin (default)')

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        limit = options.get('limit', 0) or 0
        username = options.get('username')
        only_missing = options.get('only_missing', True)

        qs = VentasUsuario.objects.all().order_by('id')
        if username:
            qs = qs.filter(nombre=username)
        if limit and limit > 0:
            qs = qs[:limit]

        total = qs.count()
        self.stdout.write(f'Found {total} ventas users to inspect')

        imported = 0
        skipped = 0
        bad_hash = 0

        for v in qs:
            uname = (v.nombre or '').strip()
            if not uname:
                self.stdout.write(self.style.WARNING(f'SKIP missing nombre id={v.id}'))
                skipped += 1
                continue

            if only_missing and UserAdminUsuario.objects.filter(username=uname).exists():
                self.stdout.write(self.style.NOTICE(f'SKIP exists: {uname}'))
                skipped += 1
                continue

            legacy_hash = getattr(v, 'contraseña', '') or ''
            # If there's no stored hash, skip
            if not legacy_hash:
                self.stdout.write(self.style.WARNING(f'SKIP no password for {uname}'))
                skipped += 1
                continue

            # Validate that the legacy hash is a recognized Django hasher
            try:
                identify_hasher(legacy_hash)
            except Exception:
                self.stdout.write(self.style.ERROR(f'BAD HASH (unrecognized) for {uname}; skipping'))
                bad_hash += 1
                continue

            if dry_run:
                self.stdout.write(self.style.SUCCESS(f'WOULD IMPORT: {uname} email={v.correo}'))
                continue

            # Perform actual import
            try:
                with transaction.atomic():
                    u = UserAdminUsuario(
                        username=uname,
                        email=(v.correo or f'{uname}@no-email.local'),
                        tipo=(getattr(v, 'tipo', 'comprador') or 'comprador'),
                        direccion=(getattr(v, 'direccion', '') or ''),
                        is_active=True,
                    )
                    # Set the password field to the legacy hash directly (don't re-hash)
                    u.password = legacy_hash
                    u.save()
                imported += 1
                self.stdout.write(self.style.SUCCESS(f'IMPORTED: {uname} -> useradmin id={u.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'ERROR importing {uname}: {e}'))

        self.stdout.write(self.style.SQL_COLTYPE(f'DONE imported={imported} skipped={skipped} bad_hash={bad_hash}'))
