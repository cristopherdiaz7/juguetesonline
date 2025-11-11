import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')
import django
django.setup()

from ventas.models import Usuario, Producto

qs = Usuario.objects.filter(nombre__startswith='sellertest')
if not qs.exists():
    print('No usuarios con nombre que empiecen por "sellertest" encontrados.')
else:
    for u in qs:
        prods = list(Producto.objects.filter(usuario=u).values_list('id', 'nombre'))
        prod_del_count, _ = Producto.objects.filter(usuario=u).delete()
        uid = u.id
        uname = u.nombre
        u.delete()
        print(f'Deleted usuario id={uid} nombre="{uname}", productos_deleted={prod_del_count}, productos={prods}')
