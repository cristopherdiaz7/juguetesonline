"""Apply the user's requested small corrections:
- Posters: 'Poster Marvel Heroes 60x90cm' -> 'Poster Venom' with asset 'venom.jpg'
- Retro: 'Radio Antiguo Coleccionable' -> 'Pistola de agua retro' with asset 'pistoladeagua.jpg'
- Vehiculos: 'Auto RC Deportivo 1:18' -> 'Auto Spiderman Involcable' with asset 'spidermaninvolcable.jpg'

The script will search products by name substring, copy the asset from frontend assets
into MEDIA_ROOT/productos/{id}_{asset} and update Producto.nombre and Producto.imagen.
"""
from pathlib import Path
import os, sys, shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from ventas.models import Producto
from django.conf import settings

FRONTEND_ASSETS = PROJECT_ROOT.parent / 'juguetesonline-frontend' / 'src' / 'assets'
MEDIA_PRODUCTOS = Path(settings.MEDIA_ROOT) / 'productos'
MEDIA_PRODUCTOS.mkdir(parents=True, exist_ok=True)

def normalize(s):
    return (s or '').lower()

def find_by_sub(s):
    s = normalize(s)
    for p in Producto.objects.all():
        if s in normalize(p.nombre):
            return p
    return None

MAPPINGS = [
    {
        'match':'Poster Marvel Heroes',
        'new_name':'Poster Venom',
        'asset':'venom.jpg',
        'categoria':'posters'
    },
    {
        'match':'Radio Antiguo Coleccionable',
        'new_name':'Pistola de Agua Retro',
        'asset':'pistoladeagua.jpg',
        'categoria':'retro'
    },
    {
        'match':'Auto RC Deportivo 1:18',
        'new_name':'Auto Spiderman Involcable',
        'asset':'spidermaninvolcable.jpg',
        'categoria':'vehiculos'
    }
]

def apply_map(m):
    p = find_by_sub(m['match'])
    if not p:
        print(f"No product found matching '{m['match']}'")
        return False
    asset = FRONTEND_ASSETS / m['asset']
    if not asset.exists():
        print(f"Asset not found: {asset}")
        return False
    dest_name = f"{p.id}_{asset.name}"
    dest = MEDIA_PRODUCTOS / dest_name
    shutil.copy2(asset, dest)
    p.nombre = m['new_name']
    p.categoria = m['categoria']
    p.imagen = f'productos/{dest_name}'
    p.save()
    print(f"Updated product {p.id}: nombre='{p.nombre}', categoria='{p.categoria}', imagen='{p.imagen}'")
    return True

def main():
    for m in MAPPINGS:
        apply_map(m)

if __name__ == '__main__':
    main()
