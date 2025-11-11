"""Restore pedidos from a backup JSON created by backup_and_delete_pedidos.py

Usage: from project root
& 'venv/Scripts/python.exe' scripts/restore_pedidos_from_backup.py scripts/backups/pedidos_backup_20251111_012622.json

This will recreate Pedido, PedidoItem, Envio, Pago rows. It will try to find existing Usuario and Producto by id; if not found, it will try to match by nombre/correo; if still not found, it will create placeholder Usuario.
"""
import os
import sys
import json
from decimal import Decimal

if len(sys.argv) < 2:
    print('Usage: restore_pedidos_from_backup.py <backup_path>')
    sys.exit(1)

backup_path = sys.argv[1]

# setup Django
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')
import django
django.setup()

from ventas.models import Pedido, PedidoItem, Envio, Pago, Usuario, Producto
from django.db import transaction, connection

with open(backup_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

pedidos = data.get('pedidos', [])
restored = 0
failed = []

for p in pedidos:
    orig_id = p.get('id')
    usuario_id = p.get('usuario_id')
    usuario_nombre = p.get('usuario_nombre')
    fecha = p.get('fecha')
    total = p.get('total')
    estado = p.get('estado')
    items = p.get('items', [])
    envio = p.get('envio')
    pagos = p.get('pagos', [])

    try:
        with transaction.atomic():
            # find or create usuario
            ventas_user = None
            if usuario_id is not None:
                ventas_user = Usuario.objects.filter(id=usuario_id).first()
            if ventas_user is None and usuario_nombre:
                ventas_user = Usuario.objects.filter(nombre=usuario_nombre).first()
            if ventas_user is None and p.get('usuario'):
                ventas_user = Usuario.objects.filter(nombre=p.get('usuario')).first()
            if ventas_user is None:
                # create placeholder user
                email = f"restored_user_{orig_id}@local.invalid"
                ventas_user = Usuario.objects.create(nombre=usuario_nombre or f'restored_user_{orig_id}', correo=email, contraseña='', direccion='restored', tipo='comprador')

            # if a pedido with same id exists, remove it first to allow exact restore
            if orig_id is not None and Pedido.objects.filter(id=orig_id).exists():
                # delete existing pedido and its related items/pagos/envio
                existing = Pedido.objects.get(id=orig_id)
                PedidoItem.objects.filter(pedido=existing).delete()
                Envio.objects.filter(pedido=existing).delete()
                Pago.objects.filter(pedido=existing).delete()
                existing.delete()

            # create Pedido with original id if provided
            if orig_id is not None:
                pedido = Pedido(id=orig_id, usuario=ventas_user, total=Decimal(str(total)) if total is not None else Decimal('0.0'), estado=estado or 'pendiente')
                pedido.save(force_insert=True)
            else:
                pedido = Pedido.objects.create(usuario=ventas_user, total=Decimal(str(total)) if total is not None else Decimal('0.0'), estado=estado or 'pendiente')

            # items
            for it in items:
                prod = None
                prod_id = it.get('producto_id')
                if prod_id:
                    prod = Producto.objects.filter(id=prod_id).first()
                if prod is None and it.get('producto_nombre'):
                    prod = Producto.objects.filter(nombre=it.get('producto_nombre')).first()
                cantidad = it.get('cantidad', 1)
                precio = Decimal(str(it.get('precio', it.get('monto', 0))))
                PedidoItem.objects.create(pedido=pedido, producto=prod, cantidad=cantidad, precio=precio)

            # envio
            if envio:
                Envio.objects.create(pedido=pedido, direccion=envio.get('direccion',''), empresa_envio=envio.get('empresa_envio',''), estado=envio.get('estado','pendiente'))

            # pagos
            for pago in pagos:
                Pago.objects.create(pedido=pedido, monto=Decimal(str(pago.get('monto', 0))), fecha=pago.get('fecha') or None, metodo_de_pago=pago.get('metodo_de_pago',''), estado=pago.get('estado',''))

            restored += 1
    except Exception as e:
        failed.append({'id': orig_id, 'error': str(e)})

# adjust AUTO_INCREMENT to max(id)+1
from django.db.models import Max

with connection.cursor() as cur:
    max_id = Pedido.objects.aggregate(max_id=Max('id'))['max_id']
    if max_id is None:
        next_val = 1
    else:
        next_val = max_id + 1
    try:
        cur.execute("ALTER TABLE %s AUTO_INCREMENT = %s" % (Pedido._meta.db_table, next_val))
        cur.execute("ALTER TABLE %s AUTO_INCREMENT = %s" % (PedidoItem._meta.db_table, 1))
    except Exception:
        pass

print(f'Restored {restored} pedidos, failed {len(failed)}')
if failed:
    print('Failures:', failed)
