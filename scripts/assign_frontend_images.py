"""Script to associate frontend asset images with Producto.imagen.

Usage (from project root):
    .\venv\Scripts\activate
    python scripts\assign_frontend_images.py

What it does:
- boots Django
- iterates Productos
- tries to find a matching file in the frontend assets folder (src/assets) by checking if any asset filename contains a normalized substring of the product name
- copies the file into MEDIA_ROOT/productos/ and sets producto.imagen to that relative path

This is a best-effort helper to seed images during development. Review results in Django admin.
"""
import os
import sys
from pathlib import Path

# adjust path to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from django.conf import settings
from ventas.models import Producto
from shutil import copy2

# frontend is sibling folder to this project root in the workspace
FRONTEND_ASSETS = PROJECT_ROOT.parent / 'juguetesonline-frontend' / 'src' / 'assets'
MEDIA_PRODUCTOS = Path(settings.MEDIA_ROOT) / 'productos'
MEDIA_PRODUCTOS.mkdir(parents=True, exist_ok=True)

def normalize(s):
    return ''.join(c for c in (s or '').lower() if c.isalnum())

def tokens(s):
    s = (s or '').lower()
    # split on non-alpha and return tokens of length>=3 sorted by length desc
    import re
    parts = re.split(r'[^a-z0-9]+', s)
    toks = [p for p in parts if len(p) >= 3]
    toks.sort(key=lambda x: -len(x))
    return toks

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
assets_list = [f for f in FRONTEND_ASSETS.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS]

# helper to find and remove an asset from the pool
def pop_asset(match_path):
    for i, p in enumerate(assets_list):
        if p == match_path:
            return assets_list.pop(i)
    return None

updated = 0
def is_image_filename(path):
    return Path(path).suffix.lower() in IMAGE_EXTS


for prod in Producto.objects.all():
    name = prod.nombre or getattr(prod, 'name', '') or ''
    cat = (prod.categoria or '').lower()
    found = None

    # skip if product already has an image and it looks valid
    try:
        if prod.imagen and is_image_filename(prod.imagen.name if hasattr(prod.imagen, 'name') else prod.imagen):
            # verify file exists in MEDIA
            media_file = Path(settings.MEDIA_ROOT) / (prod.imagen.name if hasattr(prod.imagen, 'name') else prod.imagen)
            if media_file.exists():
                print(f"Skipping product {prod.id}, already has image {prod.imagen}")
                continue
    except Exception:
        pass

    name_toks = tokens(name)

    # 1) exact filename contains normalized name
    for p in assets_list:
        fname = p.name.lower()
        if normalize(fname).find(normalize(name)) != -1:
            found = pop_asset(p)
            break

    # 2) try tokens from name (longer tokens first)
    if not found:
        for tok in name_toks:
            for p in assets_list:
                if tok in p.name.lower():
                    found = pop_asset(p)
                    break
            if found:
                break

    # 3) try category keyword in filename
    if not found and cat:
        for p in assets_list:
            if cat in p.name.lower():
                found = pop_asset(p)
                break

    # 4) fallback: pick first remaining from same category pool (heuristic)
    if not found and cat:
        cat_keywords = {
            'figuras': ['spiderman', 'batman', 'deadpool', 'hulk', 'iron', 'venom', 'iroman'],
            'peluches': ['grogu', 'stitch', 'mufasa', 'garfield', 'bobesponja', 'hellokitty'],
            'posters': ['poster', 'batman', 'naruto', 'harry', 'messi', 'stranger'],
            'retro': ['retro', 'soldaditos', 'motoplasticoretro', 'barbie', 'trompo', 'autovolveralfuturo'],
            'vehiculos': ['4x4', 'camion', 'auto', 'spidermantruck']
        }
        kws = cat_keywords.get(cat, [])
        for kw in kws:
            for p in assets_list:
                if kw in p.name.lower():
                    found = pop_asset(p)
                    break
            if found:
                break

    # 5) final fallback: take first remaining asset
    if not found and assets_list:
        found = assets_list.pop(0)

    if found:
        dest_name = f"{prod.id}_{found.name}"
        dest = MEDIA_PRODUCTOS / dest_name
        try:
            copy2(found, dest)
            prod.imagen = f'productos/{dest_name}'
            prod.save()
            updated += 1
            print(f"Assigned image for product {prod.id}: {dest_name}")
        except Exception as e:
            print(f"Failed copying {found} -> {dest}: {e}")
    else:
        print(f"No asset available for product {prod.id} - '{prod.nombre}'")

print(f"Updated images for {updated} products")
