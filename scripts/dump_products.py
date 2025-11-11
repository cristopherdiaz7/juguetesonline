"""Dump productos with id, nombre, categoria, imagen to stdout for review.

Usage:
  C:/.../venv/Scripts/python.exe scripts/dump_products.py
"""
from pathlib import Path
import os, sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from ventas.models import Producto

rows = []
for p in Producto.objects.all().order_by('id'):
    img = ''
    try:
        img = p.imagen.name if getattr(p, 'imagen', None) else ''
    except Exception:
        img = str(getattr(p, 'imagen', ''))
    rows.append((p.id, p.nombre, p.categoria, img))

for r in rows:
    print(f"ID:{r[0]:<3} | Cat:{(r[2] or '').ljust(10)} | Imagen:{r[3] or '<none>'} | Nombre: {r[1]}")

print(f"Total productos: {len(rows)}")
