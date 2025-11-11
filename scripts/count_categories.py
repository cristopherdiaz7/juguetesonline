from pathlib import Path
import os, sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from ventas.models import Producto

counts = {}
total = Producto.objects.count()
for p in Producto.objects.all():
    counts[p.categoria] = counts.get(p.categoria, 0) + 1

print('Total productos:', total)
for cat in ['figuras','peluches','posters','retro','vehiculos']:
    print(f"{cat}: {counts.get(cat,0)}")
