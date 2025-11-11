"""Finalizar mapeos pendientes: asignar candidato top (si score>=0.6) o crear nuevo producto.

Reglas:
- Si existe producto que coincide (substring) se usa.
- Else: si top candidate score >= 0.6, se asigna a ese producto.
- Else: se crea nuevo Producto con nombre canónico, categoria, precio=median(category) or 999.99, stock=10.

Copio assets desde el frontend `src/assets` y actualizo `producto.imagen`.
"""
from pathlib import Path
import os, sys, shutil
import difflib
import statistics

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from ventas.models import Producto, Usuario
from django.conf import settings

FRONTEND_ASSETS = PROJECT_ROOT.parent / 'juguetesonline-frontend' / 'src' / 'assets'
MEDIA_PRODUCTOS = Path(settings.MEDIA_ROOT) / 'productos'
MEDIA_PRODUCTOS.mkdir(parents=True, exist_ok=True)

def normalize(s):
    return ''.join(c for c in (s or '').lower() if c.isalnum())

def find_by_substring(pattern):
    pat = normalize(pattern)
    for p in Producto.objects.all():
        if pat and pat in normalize(p.nombre or ''):
            return p
    return None

def top_candidate(name):
    scores = []
    for p in Producto.objects.all():
        s = difflib.SequenceMatcher(None, normalize(name), normalize(p.nombre or '')).ratio()
        scores.append((s, p))
    scores.sort(key=lambda x: -x[0])
    return scores[0] if scores else (0, None)

MAPPINGS = [
    {'name':'Deadpool','categoria':'figuras','asset':'deadpool.jpg','canonical':'Deadpool Figura 30cm'},
    {'name':'Mujer Maravilla','categoria':'figuras','asset':'mujermaravilla.jpg','canonical':'Mujer Maravilla Figura 30cm'},
    {'name':'Harry Potter','categoria':'posters','asset':'harrypotter.jpg','canonical':'Harry Potter Poster 60x90cm'},
    {'name':'Batman Poster','categoria':'posters','asset':'posterbatman.jpg','canonical':'Poster Batman 60x90cm'},
    {'name':'Venom','categoria':'posters','asset':'venom.jpg','canonical':'Venom Poster 60x90cm'},
    {'name':'Pistola de agua','categoria':'retro','asset':'pistoladeagua.jpg','canonical':'Pistola de Agua Retro'},
    {'name':'Auto Volver al Futuro','categoria':'vehiculos','asset':'autovolveralfuturo.jpg','canonical':'Auto Volver al Futuro'},
    {'name':'Spiderman Involcable','categoria':'vehiculos','asset':'spidermaninvolcable.jpg','canonical':'Auto Spiderman Involcable'},
    {'name':'Spiderman Truck','categoria':'vehiculos','asset':'spidermantruck.jpg','canonical':'Spiderman Truck'},
]

def median_price_for_categoria(cat):
    vals = [float(p.precio) for p in Producto.objects.filter(categoria=cat) if p.precio is not None]
    if not vals:
        return 999.99
    try:
        return float(statistics.median(vals))
    except Exception:
        return float(sum(vals)/len(vals))

def get_vendedor():
    v = Usuario.objects.filter(tipo='vendedor').first()
    if v:
        return v
    return Usuario.objects.first()

def apply_mapping(m):
    name = m['name']; asset = m['asset']; cat = m['categoria']; canonical = m.get('canonical', name)

    prod = find_by_substring(name)
    if prod:
        chosen = prod
        reason = 'substring match'
    else:
        score, candidate = top_candidate(name)
        if score >= 0.6:
            chosen = candidate
            reason = f'top candidate score {score:.3f}'
        else:
            # create new
            vendedor = get_vendedor()
            precio = median_price_for_categoria(cat)
            chosen = Producto.objects.create(
                nombre=canonical,
                precio=precio,
                usuario=vendedor,
                categoria=cat,
                descripcion='',
                stock=10,
            )
            reason = 'created new product'

    src = FRONTEND_ASSETS / asset
    if not src.exists():
        print(f"Asset missing: {src} -> skipping {name}")
        return False

    dest_name = f"{chosen.id}_{src.name}"
    dest = MEDIA_PRODUCTOS / dest_name
    shutil.copy2(src, dest)

    chosen.nombre = canonical
    chosen.categoria = cat
    chosen.imagen = f'productos/{dest_name}'
    chosen.save()
    print(f"Applied {name} -> product {chosen.id} ({reason}); imagen set to {chosen.imagen}")
    return True

def dump():
    print('\nFinal dump: ID | categoria | nombre | imagen | precio')
    for p in Producto.objects.order_by('id'):
        print(f"ID:{p.id:3d} | {p.categoria:10s} | {p.nombre[:40]:40s} | {str(p.imagen)[:30]:30s} | {p.precio}")

def main():
    applied = 0
    for m in MAPPINGS:
        if apply_mapping(m):
            applied += 1
    print(f"\nDone. Applied {applied}/{len(MAPPINGS)} mappings.")
    dump()

if __name__ == '__main__':
    main()
