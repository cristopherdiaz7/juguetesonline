from django.apps import AppConfig
import os


class UseradminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'useradmin'
    
    def ready(self):
        """
        Optional startup diagnostic: if the environment variable
        `DETECT_HASHERS_ON_STARTUP` is set to a truthy value, iterate
        users and print a short report of password hash algorithms to
        stderr (so it appears in Railway logs).
        
        This is a non-invasive way to inspect legacy hash formats when
        a shell/one-off run is not available. Enable it temporarily
        and then disable it after reading the logs.
        """
        if os.getenv('DETECT_HASHERS_ON_STARTUP', 'False').lower() in ('1', 'true', 'yes'):
            try:
                # Import here to avoid side-effects at import time
                from django.contrib.auth import get_user_model
                from django.contrib.auth.hashers import identify_hasher
                
                User = get_user_model()
                users = User.objects.all()
                summary = {}
                lines = []
                for u in users:
                    pw = getattr(u, 'password', None)
                    if not pw:
                        alg = 'NO_PASSWORD'
                    else:
                        try:
                            alg = identify_hasher(pw).algorithm
                        except Exception as e:
                            alg = f'UNKNOWN:{e.__class__.__name__}'
                    lines.append(f'{u.username}\tactive={u.is_active}\thasher={alg}')
                    summary[alg] = summary.get(alg, 0) + 1
                
                import sys
                print('--- detect_password_hashers startup report ---', file=sys.stderr)
                for l in lines:
                    print(l, file=sys.stderr)
                print('\nSummary:', file=sys.stderr)
                print(f'Total users scanned: {len(lines)}', file=sys.stderr)
                for alg, count in sorted(summary.items(), key=lambda x: -x[1]):
                    print(f'  {alg}: {count}', file=sys.stderr)
                print('--- end report ---', file=sys.stderr)
            except Exception as e:
                import sys
                print('detect_password_hashers error:', e, file=sys.stderr)
