"""Detectar archivos idénticos en media/productos y listar qué productos los usan."""
from pathlib import Path
import hashlib, os, sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()
from ventas.models import Producto
from django.conf import settings

MEDIA_DIR = Path(settings.MEDIA_ROOT) / 'productos'

def sha1(p: Path):
    h = hashlib.sha1()
    with p.open('rb') as f:
        while True:
            b = f.read(8192)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

files = list(MEDIA_DIR.glob('*'))
hash_map = {}
for f in files:
    try:
        s = sha1(f)
    except Exception as e:
        s = None
    hash_map.setdefault(s, []).append(f.name)

print('Archivos totales en media/productos:', len(files))
dupes = {h: names for h, names in hash_map.items() if len(names) > 1}
if not dupes:
    print('No se encontraron archivos duplicados por contenido.')
else:
    print('Archivos duplicados detectados (por hash):')
    for h, names in dupes.items():
        print(f'Hash {h}:')
        for n in names:
            print('  -', n)

print('\nMapeo producto -> imagen actual:')
for p in Producto.objects.order_by('id'):
    print(f'ID:{p.id:3d} | imagen: {p.imagen}')
