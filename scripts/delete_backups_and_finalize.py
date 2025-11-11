"""Eliminar los archivos duplicados en media/productos/backups/ y asegurar referencias canónicas.

Precaución: este script BORRA los archivos en backups definitivamente.
"""
from pathlib import Path
import os, sys, hashlib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from ventas.models import Producto
from django.conf import settings

MEDIA_DIR = Path(settings.MEDIA_ROOT) / 'productos'
BACKUP_DIR = MEDIA_DIR / 'backups'

def sha1(p: Path):
    h = hashlib.sha1()
    with p.open('rb') as f:
        while True:
            b = f.read(8192)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def build_hash_map(dirpath):
    m = {}
    for f in Path(dirpath).glob('*'):
        if f.is_file():
            try:
                h = sha1(f)
            except Exception:
                continue
            m.setdefault(h, []).append(f)
    return m

def update_products_pointing_to_backups(canonical_map):
    # canonical_map: backup_name -> canonical_name
    updated = 0
    for p in Producto.objects.all():
        if not p.imagen:
            continue
        img = str(p.imagen)
        for backup_name, canon_name in canonical_map.items():
            if backup_name in img:
                p.imagen = f'productos/{canon_name}'
                p.save()
                updated += 1
                print(f'Producto {p.id} actualizado imagen -> productos/{canon_name}')
    print(f'Productos actualizados: {updated}')

def main():
    if not BACKUP_DIR.exists():
        print('No existe backups/ — nothing to delete.')
        return

    # map each backup file to a canonical file in MEDIA_DIR (not in backups)
    media_hash = build_hash_map(MEDIA_DIR)
    backups_hash = build_hash_map(BACKUP_DIR)

    # build reverse lookup: hash -> canonical filename (choose one in MEDIA_DIR not in backups)
    canonical = {}
    for h, files in media_hash.items():
        # prefer files not in backups dir
        for f in files:
            if 'backups' not in str(f):
                canonical[h] = f
                break

    # for each backup file, find its hash and canonical file
    canonical_map = {}
    for h, bfiles in backups_hash.items():
        can = canonical.get(h)
        if not can:
            # no canonical in media (unlikely) — skip deletion of this backup
            print(f'No canonical file found for hash {h}; skipping backups: {[str(b) for b in bfiles]}')
            continue
        for bf in bfiles:
            canonical_map[bf.name] = can.name

    # update any product.imagen that points to backups to point to canonical
    update_products_pointing_to_backups(canonical_map)

    # delete all files in backups
    deleted = 0
    for f in BACKUP_DIR.glob('*'):
        try:
            f.unlink()
            deleted += 1
            print(f'Deleted backup file: {f.name}')
        except Exception as e:
            print(f'Failed to delete {f}: {e}')

    # remove backups dir if empty
    try:
        BACKUP_DIR.rmdir()
        print('Removed backups directory.')
    except Exception:
        print('Backups directory not removed (may contain subdirs).')

    # final duplicate check
    media_hash_after = build_hash_map(MEDIA_DIR)
    dupes = {h:files for h, files in media_hash_after.items() if len(files) > 1}
    if not dupes:
        print('No duplicate files remain in media/productos.')
    else:
        print('Duplicates still present after deletion:')
        for h, files in dupes.items():
            print(h, [f.name for f in files])

    print(f'Deleted {deleted} backup files.')

if __name__ == "__main__":
    main()
