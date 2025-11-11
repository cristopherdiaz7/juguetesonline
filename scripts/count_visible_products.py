from pathlib import Path
import os, sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from ventas.models import Producto

qs = Producto.objects.exclude(nombre__istartswith='OLD - ')
print('Visible total (no OLD):', qs.count())
for cat in ['figuras','peluches','posters','retro','vehiculos']:
    print(cat, qs.filter(categoria=cat).count())
