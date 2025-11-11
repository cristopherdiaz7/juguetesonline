"""Backup all Pedido and related data to scripts/backups/pedidos_backup_<ts>.json
and then DELETE all Pedido and PedidoItem rows.

Usage (from repo root):
  & 'venv/Scripts/python.exe' scripts/backup_and_delete_pedidos.py

This script configures Django, writes the backup, then deletes.
"""
import os
import sys
import json
import datetime
from decimal import Decimal

# ensure project root on sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')
import django
django.setup()

from ventas.models import Pedido, PedidoItem, Envio, Pago

# ensure backups dir
backups_dir = os.path.join(project_root, 'scripts', 'backups')
os.makedirs(backups_dir, exist_ok=True)

ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup_path = os.path.join(backups_dir, f'pedidos_backup_{ts}.json')

payload = []
for p in Pedido.objects.all():
    obj = {
        'id': p.id,
        'usuario_id': p.usuario.id if p.usuario else None,
        'usuario_nombre': getattr(p.usuario, 'nombre', None) if p.usuario else None,
        'fecha': p.fecha.isoformat() if getattr(p, 'fecha', None) else None,
        'total': float(p.total) if isinstance(p.total, Decimal) else p.total,
        'estado': p.estado,
        'items': [],
        'envio': None,
        'pagos': []
    }
    for it in PedidoItem.objects.filter(pedido=p):
        obj['items'].append({
            'id': it.id,
            'producto_id': it.producto.id if it.producto else None,
            'producto_nombre': it.producto.nombre if it.producto else None,
            'cantidad': it.cantidad,
            'precio': float(it.precio) if isinstance(it.precio, Decimal) else it.precio,
        })
    try:
        env = Envio.objects.filter(pedido=p).first()
        if env:
            obj['envio'] = {
                'id': env.id,
                'direccion': env.direccion,
                'empresa_envio': env.empresa_envio,
                'estado': env.estado,
            }
    except Exception:
        pass
    try:
        pagos = Pago.objects.filter(pedido=p)
        for pago in pagos:
            obj['pagos'].append({
                'id': pago.id,
                'monto': float(pago.monto) if isinstance(pago.monto, Decimal) else pago.monto,
                'fecha': pago.fecha.isoformat() if getattr(pago, 'fecha', None) else None,
                'metodo_de_pago': pago.metodo_de_pago,
                'estado': pago.estado,
            })
    except Exception:
        pass
    payload.append(obj)

# write backup
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump({'exported_at': datetime.datetime.now().isoformat(), 'pedidos': payload}, f, ensure_ascii=False, indent=2)

print(f'Backup written to: {backup_path} (pedidos={len(payload)})')

# delete PedidoItem and Pedido
items_deleted = 0
pedidos_deleted = 0

try:
    items_deleted, _ = PedidoItem.objects.all().delete()
    pedidos_deleted, _ = Pedido.objects.all().delete()
except Exception as e:
    print('Error deleting rows:', str(e))

print(f'Deleted: PedidoItem rows deleted ~ {items_deleted}, Pedido rows deleted ~ {pedidos_deleted}')
print('Done.')
