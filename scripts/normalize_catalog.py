"""Normalizar catálogo al conjunto final de 27 productos y deduplicar media/productos.

Reglas:
- Mantener sólo los productos canónicos (ids predefinidos) y marcar el resto como OLD - (no borrar).
- Deduplicar archivos en media/productos: elegir archivo canónico por hash y actualizar referencias.
- Mover archivos redundantes a media/productos/backups/ para recuperación.
"""
from pathlib import Path
import os, sys, shutil, hashlib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from ventas.models import Producto
from django.conf import settings

MEDIA_DIR = Path(settings.MEDIA_ROOT) / 'productos'
BACKUP_DIR = MEDIA_DIR / 'backups'
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Keep set chosen to match desired distribution (27 products)
KEEP_IDS = set([
    # figuras (5)
    1,2,3,51,52,
    # peluches (7)
    11,12,13,14,15,16,25,
    # posters (6)
    5,21,24,53,58,26,
    # retro (5)
    31,32,33,35,37,
    # vehiculos (4)
    48,41,57,59,
])

def sha1(path: Path):
    h = hashlib.sha1()
    with path.open('rb') as f:
        while True:
            b = f.read(8192)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def mark_old_products():
    for p in Producto.objects.all():
        if p.id in KEEP_IDS:
            continue
        # mark as old
        if not (p.nombre or '').startswith('OLD - '):
            p.nombre = f'OLD - {p.nombre}'
        p.imagen = None
        p.stock = 0
        p.save()
    print('Marcados productos no-keep como OLD (imagen=None, stock=0).')

def dedupe_media():
    files = [f for f in MEDIA_DIR.iterdir() if f.is_file()]
    hash_map = {}
    for f in files:
        try:
            h = sha1(f)
        except Exception:
            continue
        hash_map.setdefault(h, []).append(f)

    # build filename -> canonical mapping
    rename_map = {}
    for h, flist in hash_map.items():
        if len(flist) <= 1:
            continue
        # prefer canonical file whose prefix id is in KEEP_IDS
        canonical = None
        for f in flist:
            name = f.name
            if name.split('_')[0].isdigit() and int(name.split('_')[0]) in KEEP_IDS:
                canonical = f
                break
        if not canonical:
            # otherwise choose first
            canonical = flist[0]
        for f in flist:
            if f == canonical:
                continue
            # move redundant file to backup
            dest = BACKUP_DIR / f.name
            shutil.move(str(f), str(dest))
            print(f'Moved duplicate {f.name} -> backups/{f.name}')
            # update any Producto pointing to this file to point to canonical
            rel_old = f.name
            rel_can = canonical.name
            for p in Producto.objects.filter(imagen__contains=rel_old):
                p.imagen = f'productos/{rel_can}'
                p.save()
                print(f'Updated Producto ID {p.id} imagen -> productos/{rel_can}')

    print('Dedupe media completa. Copias redundantes movidas a backups/.')

def final_counts():
    counts = {}
    total = Producto.objects.count()
    for p in Producto.objects.all():
        counts[p.categoria] = counts.get(p.categoria, 0) + 1
    print('\nTotal productos:', total)
    for cat in ['figuras','peluches','posters','retro','vehiculos']:
        print(f"{cat}: {counts.get(cat,0)}")

def main():
    mark_old_products()
    dedupe_media()
    final_counts()

if __name__ == '__main__':
    main()
