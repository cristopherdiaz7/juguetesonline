"""Apply manual product -> image/category/name mappings provided by user.

This script will:
- search for the best matching Producto by name (fuzzy containment)
- update its `nombre`, `categoria`, and `imagen` fields
- copy the image from frontend assets into MEDIA_ROOT/productos/{id}_{filename}

Safe: it will print actions and only modify DB for matched products.

Run: venv\Scripts\python.exe scripts\apply_manual_mappings.py
"""
from pathlib import Path
import os, sys, shutil
import re

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
    return ''.join(c for c in (s or '').lower() if c.isalnum())

def find_best_product_by_name(pattern):
    """Return Producto instance whose nombre best matches pattern by containment length."""
    pat = normalize(pattern)
    candidates = []
    for p in Producto.objects.all():
        name = normalize(p.nombre or '')
        if pat and pat in name:
            candidates.append((len(pat), p))
    if candidates:
        # return first best (longest match)
        candidates.sort(key=lambda x: -x[0])
        return candidates[0][1]
    # fallback: try token containment
    toks = [t for t in re.split(r'[^a-z0-9]+', pat) if len(t) >= 3]
    for t in toks:
        for p in Producto.objects.all():
            if t in normalize(p.nombre or ''):
                return p
    return None

# Manual mapping provided by user
MAPPINGS = [
    # figuras
    {'name':'Spiderman','categoria':'figuras','asset':'spiderman.jpg','canonical':'Spiderman'},
    {'name':'Batman','categoria':'figuras','asset':'batman.jpg','canonical':'Batman Figura De Acción 30cm'},
    {'name':'Iron Man','categoria':'figuras','asset':'iroman.jpg','canonical':'Iron Man Deluxe 30cm'},
    {'name':'Deadpool','categoria':'figuras','asset':'deadpool.jpg','canonical':'Deadpool Figura 30cm'},
    {'name':'Mujer Maravilla','categoria':'figuras','asset':'mujermaravilla.jpg','canonical':'Mujer Maravilla Figura 30cm'},

    # peluches
    {'name':'Bob Esponja','categoria':'peluches','asset':'bobesponja.jpg','canonical':'Peluche Bob Esponja 40cm'},
    {'name':'Grogu','categoria':'peluches','asset':'grogu.jpg','canonical':'Grogu Peluche 40cm'},
    {'name':'Stitch','categoria':'peluches','asset':'stitch.jpg','canonical':'Stitch Peluche 35cm'},
    {'name':'Mufasa','categoria':'peluches','asset':'mufasa.jpg','canonical':'Mufasa Peluche 45cm'},
    {'name':'Garfield','categoria':'peluches','asset':'garfield.jpg','canonical':'Garfield Peluche 30cm'},
    {'name':'Hello Kitty','categoria':'peluches','asset':'hellokitty.jpg','canonical':'Hello Kitty Peluche 30cm'},
    {'name':'Messi','categoria':'peluches','asset':'messi.jpg','canonical':'Messi Peluche 40cm'},

    # posters
    {'name':'Harry Potter','categoria':'posters','asset':'harrypotter.jpg','canonical':'Harry Potter Poster 60x90cm'},
    {'name':'Hulk','categoria':'posters','asset':'hulkcomics.jpg','canonical':'Hulk Comics Poster 60x90cm'},
    {'name':'Naruto','categoria':'posters','asset':'naruto.jpg','canonical':'Naruto Poster 60x90cm'},
    {'name':'Batman Poster','categoria':'posters','asset':'posterbatman.jpg','canonical':'Poster Batman 60x90cm'},
    {'name':'Stranger Things','categoria':'posters','asset':'strangerthings.jpg','canonical':'Stranger Things Poster 60x90cm'},
    {'name':'Venom','categoria':'posters','asset':'venom.jpg','canonical':'Venom Poster 60x90cm'},

    # retro
    {'name':'Trompo Retro','categoria':'retro','asset':'tromporetro.jpg','canonical':'Trompo Retro Edición Limitada'},
    {'name':'Soldaditos Retro','categoria':'retro','asset':'soldaditosretro.jpg','canonical':'Soldaditos Retro Edición Limitada'},
    {'name':'Moto Plástico Retro','categoria':'retro','asset':'motoplasticoretro.jpg','canonical':'Moto Plástico Retro'},
    {'name':'Pistola de agua','categoria':'retro','asset':'pistoladeagua.jpg','canonical':'Pistola de Agua Retro'},
    {'name':'Star Wars muñeco','categoria':'retro','asset':'starwars.jpg','canonical':'Muñeco Star Wars Retro'},

    # vehiculos
    {'name':'Camioneta 4x4','categoria':'vehiculos','asset':'4x4rojo.jpg','canonical':'Camioneta 4x4 Rojo'},
    {'name':'Auto Volver al Futuro','categoria':'vehiculos','asset':'autovolveralfuturo.jpg','canonical':'Auto Volver al Futuro'},
    {'name':'Spiderman Involcable','categoria':'vehiculos','asset':'spidermaninvolcable.jpg','canonical':'Auto Spiderman Involcable'},
    {'name':'Spiderman Truck','categoria':'vehiculos','asset':'spidermantruck.jpg','canonical':'Spiderman Truck'},
]

def apply_mapping(m):
    target_name = m['name']
    asset = m['asset']
    categoria = m['categoria']
    canonical = m.get('canonical') or target_name

    prod = find_best_product_by_name(target_name)
    if not prod:
        print(f"No product found matching '{target_name}'")
        return False

    # copy asset
    src = FRONTEND_ASSETS / asset
    if not src.exists():
        print(f"Asset not found: {src}")
        return False

    dest_name = f"{prod.id}_{src.name}"
    dest = MEDIA_PRODUCTOS / dest_name
    shutil.copy2(src, dest)

    # update product
    prod.nombre = canonical
    prod.categoria = categoria
    prod.imagen = f'productos/{dest_name}'
    prod.save()
    print(f"Updated product {prod.id}: set nombre='{prod.nombre}', categoria='{prod.categoria}', imagen='{prod.imagen}'")
    return True

def main():
    successes = 0
    failures = []
    for m in MAPPINGS:
        ok = apply_mapping(m)
        if ok:
            successes += 1
        else:
            failures.append(m)
    print(f"Done. Successes: {successes}. Failures: {len(failures)}")
    if failures:
        print("Failed mappings:")
        for f in failures:
            print(f)

if __name__ == '__main__':
    main()
