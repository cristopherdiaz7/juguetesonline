"""Backup y eliminación definitiva de productos marcados como 'OLD - '.

Acciones:
- Exporta los productos OLD a un JSON backup en scripts/backups/old_products_YYYYmmdd_HHMMSS.json
- Mueve cualquier archivo de imagen asociado (si existe) a scripts/backups/images/
- Borra los registros de Producto correspondientes de la base de datos.

Precaución: irreversible sin restauración desde el JSON.
"""
from pathlib import Path
import os, sys, shutil, json
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from ventas.models import Producto
from django.conf import settings
from django.core import serializers

BACKUP_DIR = PROJECT_ROOT / 'scripts' / 'backups'
BACKUP_IMAGES = BACKUP_DIR / 'images'
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_IMAGES.mkdir(parents=True, exist_ok=True)

def backup_and_delete():
    qs = Producto.objects.filter(nombre__istartswith='OLD - ')
    total = qs.count()
    if total == 0:
        print('No OLD products found; nothing to delete.')
        return

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_path = BACKUP_DIR / f'old_products_{ts}.json'

    # Serialize queryset to JSON
    with json_path.open('wb') as f:
        data = serializers.serialize('json', qs)
        f.write(data.encode('utf-8'))

    # Move associated image files (if any)
    moved = 0
    for p in qs:
        if p.imagen:
            img_path = Path(settings.MEDIA_ROOT) / str(p.imagen)
            if img_path.exists():
                dest = BACKUP_IMAGES / img_path.name
                shutil.move(str(img_path), str(dest))
                moved += 1

    # Delete the queryset
    ids = list(qs.values_list('id', flat=True))
    qs.delete()

    print(f'Backed up {total} products to {json_path}')
    print(f'Moved {moved} image files to {BACKUP_IMAGES}')
    print(f'Deleted products IDs: {ids}')

if __name__ == '__main__':
    backup_and_delete()
