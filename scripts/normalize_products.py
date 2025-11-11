"""Normalize products to canonical lists (10 per category) and assign matching images.

This will update existing Producto rows (IDs 1..50) to a known canonical set.
It copies matching frontend assets into MEDIA/productos/{id}_{assetname} and sets Producto.imagen accordingly.

Run: venv\Scripts\python.exe scripts\normalize_products.py
"""
from pathlib import Path
import os, sys, re

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from ventas.models import Producto, Usuario
from django.conf import settings
from shutil import copy2

FRONTEND_ASSETS = PROJECT_ROOT.parent / 'juguetesonline-frontend' / 'src' / 'assets'
MEDIA_PRODUCTOS = Path(settings.MEDIA_ROOT) / 'productos'
MEDIA_PRODUCTOS.mkdir(parents=True, exist_ok=True)

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def normalize(s):
    return ''.join(c for c in (s or '').lower() if c.isalnum())

assets = [p for p in FRONTEND_ASSETS.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]

# canonical product data: 10 per category
canonical = {
    'figuras': [
        ('Spiderman Figura 30cm', 90000),
        ('Batman Figura 30cm', 85000),
        ('Iron Man Deluxe 30cm', 95000),
        ('Captain America Escudo 30cm', 88000),
        ('Hulk Smash Figura 30cm', 92000),
        ('Thor Figura Con Martillo 30cm', 90000),
        ('Black Panther Figura 30cm', 87000),
        ('Wonder Woman Figura 30cm', 86000),
        ('Flash Speedster Figura 30cm', 82000),
        ('Green Lantern Figura 30cm', 80000),
    ],
    'peluches': [
        ('Grogu Peluche 40cm', 25000),
        ('Stitch Peluche 35cm', 22000),
        ('Mufasa Peluche 45cm', 24000),
        ('Garfield Peluche 30cm', 18000),
        ('Bob Esponja Peluche 40cm', 20000),
        ('Hello Kitty Peluche 30cm', 19000),
        ('Elefante Peluche 55cm', 30000),
        ('Oveja Peluche 30cm', 17000),
        ('Dinosaurio Peluche 45cm', 26000),
        ('Panda Peluche 50cm', 28000),
    ],
    'posters': [
        ('Poster Naruto 60x90cm', 5000),
        ('Poster Star Wars 60x90cm', 5500),
        ('Poster Batman 60x90cm', 5200),
        ('Poster Stranger Things 60x90cm', 4800),
        ('Poster Messi 60x90cm', 5300),
        ('Poster Marvel Heroes 60x90cm', 6000),
        ('Poster Retro 80s 60x90cm', 4500),
        ('Poster Música Clásica 60x90cm', 4700),
        ('Poster Deportes 60x90cm', 5100),
        ('Poster Paisaje Fotográfico 60x90cm', 4900),
    ],
    'retro': [
        ('Trompo Retro Edición Limitada', 12000),
        ('Soldaditos Retro Edición Limitada', 14000),
        ('Moto Plástico Retro', 13000),
        ('Barbie Retro Juego de Mesa', 15000),
        ('Radio Antiguo Coleccionable', 11000),
        ('Lego Vintage Set', 22000),
        ('Muñeco Retro 1980', 12500),
        ('Máquina de Pinball Mini', 45000),
        ('Cassette Classic Pack', 8000),
        ('Camión Metal Antiguo', 21000),
    ],
    'vehiculos': [
        ('Auto RC Deportivo 1:18', 45000),
        ('Camión de Bomberos Metal 1:24', 42000),
        ('Helicóptero RC 1:16', 47000),
        ('Moto RC 1:12', 23000),
        ('Barco Velero RC 1:20', 39000),
        ('Tractor Agrícola 1:16', 34000),
        ('Coche de Carrera 1:24', 41000),
        ('Camioneta 4x4 RC 1:18', 44000),
        ('Remolque y Trailer Set', 38000),
        ('Autobus Escolar Metal 1:20', 36000),
    ],
}

# flatten canonical into ordered list matching product id ranges
ordered = []
for cat in ['figuras','peluches','posters','retro','vehiculos']:
    for name, price in canonical[cat]:
        ordered.append((cat, name, price))

# ensure enough products exist
total_needed = len(ordered)
existing = list(Producto.objects.all().order_by('id'))
if len(existing) < total_needed:
    # create missing products using first seller
    seller = Usuario.objects.first()
    for i in range(len(existing), total_needed):
        Producto.objects.create(nombre='placeholder', precio=1000, usuario=seller, descripcion='', stock=10, categoria='figuras')
    existing = list(Producto.objects.all().order_by('id'))

def find_asset_for_name(name):
    name_norm = normalize(name)
    # exact match best
    for p in assets:
        if name_norm in p.name.lower():
            return p
    # token match
    toks = re.split(r'[^a-z0-9]+', name.lower())
    toks = [t for t in toks if len(t)>=3]
    for t in toks:
        for p in assets:
            if t in p.name.lower():
                return p
    # fallback by category keyword
    return None

assigned = 0
for idx, prod in enumerate(existing[:total_needed]):
    cat, name, price = ordered[idx]
    prod.nombre = name
    prod.precio = price
    prod.categoria = cat
    prod.descripcion = f'Producto {name} en categoría {cat}.'
    prod.stock = 20
    # find asset
    asset = find_asset_for_name(name)
    if not asset:
        # try category-based fallbacks
        for p in assets:
            if cat in p.name.lower():
                asset = p
                break
    if asset:
        dest_name = f"{prod.id}_{asset.name}"
        dest = MEDIA_PRODUCTOS / dest_name
        try:
            copy2(asset, dest)
            prod.imagen = f'productos/{dest_name}'
        except Exception as e:
            print('Failed copy for', prod.id, e)
    else:
        prod.imagen = None
    prod.save()
    assigned += 1

print(f'Normalized {assigned} products to canonical set.')
