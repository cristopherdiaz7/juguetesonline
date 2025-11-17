from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher


class Command(BaseCommand):
    help = (
        "Detect password hash algorithms used by users and optionally test a password for one user.\n"
        "Useful to identify legacy hash formats after a migration/import."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--username', '-u', dest='username', help='If provided, show only this user.'
        )
        parser.add_argument(
            '--test-password', '-p', dest='test_password', help='(Optional) test this password against the given --username. WARNING: do not use in shared logs.'
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options.get('username')
        test_password = options.get('test_password')

        users = User.objects.all()
        if username:
            users = users.filter(username=username)

        summary = {}
        total = 0
        for u in users:
            total += 1
            pw = getattr(u, 'password', None)
            if not pw:
                alg = 'NO_PASSWORD'
            else:
                try:
                    alg = identify_hasher(pw).algorithm
                except Exception as e:
                    alg = f'UNKNOWN:{e.__class__.__name__}'

            self.stdout.write(f'{u.username}\tactive={u.is_active}\thasher={alg}')
            summary[alg] = summary.get(alg, 0) + 1

            if test_password and username:
                # Only test when a single username is provided and a test password.
                try:
                    matches = u.check_password(test_password)
                except Exception as e:
                    matches = False
                self.stdout.write(f'--> password_matches={matches}')

        # Print summary
        self.stdout.write('\nSummary:')
        self.stdout.write(f'Total users scanned: {total}')
        for alg, count in sorted(summary.items(), key=lambda x: -x[1]):
            self.stdout.write(f'  {alg}: {count}')

        if total == 0:
            self.stdout.write('No users found with the given filter.')
