#!/usr/bin/env python3
"""
Borra usuarios de ventas.Usuario por username o correo.
Uso: ejecutar desde la raíz del repo con el python del venv, por ejemplo:
    & .\venv\Scripts\python.exe scripts/delete_users.py

El script intentará localizar usuarios por username o correo y los eliminará.
Imprime un resumen de lo eliminado.
"""
import sys
import pathlib
import os
import json
from datetime import datetime

if __name__ == '__main__':
    # asegurar que la raíz del repo está en sys.path para importar el paquete juguetesonline
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))

    # configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')
    import django
    django.setup()

    # import both possible user models (ventas.Usuario used in some scripts, and useradmin.Usuario as project auth user)
    from ventas.models import Usuario as VentasUsuario
    try:
        from useradmin.models import Usuario as AuthUsuario
    except Exception:
        AuthUsuario = None

    # lista de usuarios a eliminar: (username, email) pares - si uno está vacío, se ignora
    targets = [
        ("usuario1", "usuario1@ejemplo.com"),
        ("usuario_jwt_2024", "usuario_jwt@ejemplo.com"),
        ("prueba123", "prueba@gmail.com"),
        ("cristodiaz", "crist@example.com"),
        ("testbuyer1", "tb1@example.com"),
    ]

    deleted = []
    skipped = []
    for uname, email in targets:
        found_any = False

        # buscar en useradmin.Usuario (auth user)
        if AuthUsuario is not None:
            try:
                auth_qs = AuthUsuario.objects.none()
                if uname:
                    auth_qs = AuthUsuario.objects.filter(username__iexact=uname)
                if email:
                    auth_qs = auth_qs | AuthUsuario.objects.filter(email__iexact=email)
                if auth_qs.exists():
                    found_any = True
                    for u in auth_qs.distinct():
                        try:
                            info = {'model': 'auth.Usuario', 'id': u.id, 'username': u.username, 'email': u.email}
                            print(f"Borrando (auth) usuario: {info}")
                            deleted.append(info)
                            u.delete()
                        except Exception as e:
                            print(f"Error borrando usuario auth {u}: {e}")
                            skipped.append({'username': getattr(u, 'username', None), 'email': getattr(u, 'email', None), 'error': str(e)})
            except Exception as e:
                print(f"Error buscando en auth {uname} / {email}: {e}")
                skipped.append({'username': uname, 'email': email, 'error': str(e)})

        # buscar en ventas.Usuario (modelo histórico de ventas)
        try:
            ventas_qs = VentasUsuario.objects.none()
            if uname:
                ventas_qs = VentasUsuario.objects.filter(nombre__iexact=uname)
            if email:
                ventas_qs = ventas_qs | VentasUsuario.objects.filter(correo__iexact=email)
            if ventas_qs.exists():
                found_any = True
                for u in ventas_qs.distinct():
                    try:
                        info = {'model': 'ventas.Usuario', 'id': u.id, 'nombre': u.nombre, 'correo': u.correo}
                        print(f"Borrando (ventas) usuario: {info}")
                        deleted.append(info)
                        u.delete()
                    except Exception as e:
                        print(f"Error borrando usuario ventas {u}: {e}")
                        skipped.append({'username': getattr(u, 'nombre', None), 'email': getattr(u, 'correo', None), 'error': str(e)})
        except Exception as e:
            print(f"Error buscando en ventas {uname} / {email}: {e}")
            skipped.append({'username': uname, 'email': email, 'error': str(e)})

        if not found_any:
            print(f"No encontrado: {uname} / {email}")
            skipped.append({'username': uname, 'email': email})

    # escribir un backup resumen en scripts/backups
    try:
        os.makedirs('scripts/backups', exist_ok=True)
        out = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'deleted': deleted,
            'skipped': skipped,
        }
        fname = f"scripts/backups/deleted_users_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"Resumen escrito en: {fname}")
    except Exception as e:
        print(f"No se pudo escribir backup: {e}")

    print(f"Hecho. Eliminados: {len(deleted)}. Omitidos/no encontrados: {len(skipped)}.")
