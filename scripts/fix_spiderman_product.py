"""Reparar producto 1 (Spiderman) que fue sobrescrito por el mapeo final.

Acciones:
- Crear un nuevo producto para 'Auto Spiderman Involcable' si no existe.
- Mover la imagen asignada accidentalmente (productos/1_spidermaninvolcable.jpg)
  a productos/{newid}_spidermaninvolcable.jpg y asignarla al nuevo producto.
- Restablecer el producto ID=1 a nombre 'Spiderman', categoria 'figuras' y
  imagen 'productos/1_spiderman.jpg'.
"""
from pathlib import Path
import os, sys, shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from ventas.models import Producto, Usuario
from django.conf import settings

MEDIA_PRODUCTOS = Path(settings.MEDIA_ROOT) / 'productos'

def get_vendedor():
    v = Usuario.objects.filter(tipo='vendedor').first()
    if v:
        return v
    return Usuario.objects.first()

def main():
    try:
        p1 = Producto.objects.get(id=1)
    except Producto.DoesNotExist:
        print('Producto ID=1 no existe; nada que reparar.')
        return

    # Paths
    file_invol = MEDIA_PRODUCTOS / '1_spidermaninvolcable.jpg'
    desired_p1_img = 'productos/1_spiderman.jpg'
    desired_p1_name = 'Spiderman'
    desired_p1_cat = 'figuras'

    # If invol image exists, create new product and move file
    if file_invol.exists():
        vendedor = get_vendedor()
        price = Producto.objects.filter(categoria='vehiculos').first().precio if Producto.objects.filter(categoria='vehiculos').exists() else 40000
        newp = Producto.objects.create(
            nombre='Auto Spiderman Involcable',
            precio=price,
            usuario=vendedor,
            categoria='vehiculos',
            descripcion='Auto Spiderman involcable',
            stock=5,
        )
        new_name = f"{newp.id}_spidermaninvolcable.jpg"
        new_path = MEDIA_PRODUCTOS / new_name
        shutil.move(str(file_invol), str(new_path))
        newp.imagen = f'productos/{new_name}'
        newp.save()
        print(f'Creado producto {newp.id} y asignada imagen {newp.imagen}')
    else:
        print('No existe archivo productos/1_spidermaninvolcable.jpg; no se creó producto involcable.')

    # Restore product 1
    p1.nombre = desired_p1_name
    p1.categoria = desired_p1_cat
    # Ensure original image exists
    orig = MEDIA_PRODUCTOS / '1_spiderman.jpg'
    if orig.exists():
        p1.imagen = desired_p1_img
    else:
        print('Advertencia: falta media/productos/1_spiderman.jpg; dejar imagen vacía')
        p1.imagen = None
    p1.save()
    print('Producto 1 restaurado a Spiderman (figuras).')

if __name__ == '__main__':
    main()
