import os
import django
import decimal
from types import SimpleNamespace

import sys
# ensure project root is on sys.path so Django settings can be imported
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')
django.setup()

from ventas.models import Usuario, Producto
from ventas.serializer import PedidoSerializer

# Crear usuario comprador y vendedor de prueba
comprador = Usuario.objects.create(nombre='shellbuyer', correo='shellbuyer@example.test', contraseña='', direccion='X', tipo='comprador')
vendedor = Usuario.objects.create(nombre='sellertest', correo='sellertest@example.test', contraseña='', direccion='Y', tipo='vendedor')

# Crear producto con stock 5 vinculado al vendedor
prod = Producto.objects.create(nombre='Producto Test Shell', precio=decimal.Decimal('100.00'), usuario=vendedor, categoria='figuras', descripcion='desc', stock=5)

# Preparar payload para crear pedido con 2 unidades
payload = {'items':[{'id': prod.id, 'cantidad':2, 'precio':100.0}], 'total':200.0, 'estado':'pendiente'}

# Simular request contexto con user cuyo username coincide con comprador.nombre
request = SimpleNamespace(user=SimpleNamespace(is_authenticated=True, username='shellbuyer'), data={})
ser = PedidoSerializer(data=payload, context={'request': request})
if ser.is_valid():
    pedido = ser.save()
    print('Pedido creado id=', pedido.id, 'total=', pedido.total)
    items = list(pedido.items.all())
    print('Items count:', len(items))
    for it in items:
        print('Item:', it.producto.nombre if it.producto else None, it.cantidad, it.precio)
    # verificar stock del producto
    prod.refresh_from_db()
    print('Stock restante del producto:', prod.stock)
else:
    print('Errores serializer:', ser.errors)
