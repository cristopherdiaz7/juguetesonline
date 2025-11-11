"""Fix image assignments by unassigning images that don't match product name or category.

This is conservative: it only sets producto.imagen = None (doesn't delete files).
Run with venv python from project root.
"""
from pathlib import Path
import os, sys, re

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from ventas.models import Producto
from django.conf import settings

def tokens(s):
    s = (s or '').lower()
    parts = re.split(r'[^a-z0-9]+', s)
    toks = [p for p in parts if len(p) >= 3]
    toks.sort(key=lambda x: -len(x))
    return toks

cat_keywords = {
    'figuras': ['spider', 'batman', 'iron', 'hulk', 'deadpool', 'venom', 'flash', 'green', 'lantern', 'thor'],
    'peluches': ['grogu', 'stitch', 'mufasa', 'garfield', 'bobesponja', 'hellokitty', 'peluche'],
    'posters': ['poster', 'poster', 'naruto', 'star', 'stranger', 'harry', 'messi', 'poster'],
    'retro': ['retro', 'trompo', 'soldaditos', 'barbie', 'motoplastic', 'cassette', 'lego', 'vintage'],
    'vehiculos': ['4x4', 'auto', 'camion', 'truck', 'rc', 'remolque', 'tractor', 'autobus']
}

changed = 0
skipped = 0
for p in Producto.objects.all():
    img_name = None
    try:
        img_name = p.imagen.name if getattr(p, 'imagen', None) else None
    except Exception:
        img_name = None
    if not img_name:
        skipped += 1
        continue
    # strip possible prefix 'productos/{id}_'
    fname = Path(img_name).name.lower()
    # remove leading numeric id and underscore if present
    fname_noprefix = re.sub(r'^\d+_', '', fname)

    name_toks = tokens(p.nombre or '')
    cat = (p.categoria or '').lower()
    ok = False

    # 1) any token from name in filename
    for tok in name_toks:
        if tok in fname_noprefix:
            ok = True
            break

    # 2) any category keyword in filename
    if not ok and cat in cat_keywords:
        for kw in cat_keywords[cat]:
            if kw in fname_noprefix:
                ok = True
                break

    # 3) special-case: posters often have 'poster' or known artist
    if not ok and cat == 'posters' and 'poster' in fname_noprefix:
        ok = True

    if not ok:
        print(f"Unassigning image for product {p.id}: {p.nombre} (was {img_name})")
        p.imagen = None
        p.save()
        changed += 1
    else:
        skipped += 1

print(f"Done. Images unassigned: {changed}. Kept/none: {skipped}.")
