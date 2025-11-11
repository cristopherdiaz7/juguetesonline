"""Proponer candidatos para mappings fallidos usando similitud de cadenas.

Imprime para cada mapping la lista de hasta 5 mejores productos (id, nombre, categoria, score).
"""
from pathlib import Path
import os, sys
import difflib
import re

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juguetesonline.settings')

import django
django.setup()

from ventas.models import Producto

def normalize(s):
    return ''.join(c for c in (s or '').lower() if c.isalnum())

MAPPINGS = [
    # (same list used previously) figuras
    {'name':'Spiderman','categoria':'figuras','asset':'spiderman.jpg'},
    {'name':'Batman','categoria':'figuras','asset':'batman.jpg'},
    {'name':'Iron Man','categoria':'figuras','asset':'iroman.jpg'},
    {'name':'Deadpool','categoria':'figuras','asset':'deadpool.jpg'},
    {'name':'Mujer Maravilla','categoria':'figuras','asset':'mujermaravilla.jpg'},
    # peluches
    {'name':'Bob Esponja','categoria':'peluches','asset':'bobesponja.jpg'},
    {'name':'Grogu','categoria':'peluches','asset':'grogu.jpg'},
    {'name':'Stitch','categoria':'peluches','asset':'stitch.jpg'},
    {'name':'Mufasa','categoria':'peluches','asset':'mufasa.jpg'},
    {'name':'Garfield','categoria':'peluches','asset':'garfield.jpg'},
    {'name':'Hello Kitty','categoria':'peluches','asset':'hellokitty.jpg'},
    {'name':'Messi','categoria':'peluches','asset':'messi.jpg'},
    # posters
    {'name':'Harry Potter','categoria':'posters','asset':'harrypotter.jpg'},
    {'name':'Hulk','categoria':'posters','asset':'hulkcomics.jpg'},
    {'name':'Naruto','categoria':'posters','asset':'naruto.jpg'},
    {'name':'Batman Poster','categoria':'posters','asset':'posterbatman.jpg'},
    {'name':'Stranger Things','categoria':'posters','asset':'strangerthings.jpg'},
    {'name':'Venom','categoria':'posters','asset':'venom.jpg'},
    # retro
    {'name':'Trompo Retro','categoria':'retro','asset':'tromporetro.jpg'},
    {'name':'Soldaditos Retro','categoria':'retro','asset':'soldaditosretro.jpg'},
    {'name':'Moto Plástico Retro','categoria':'retro','asset':'motoplasticoretro.jpg'},
    {'name':'Pistola de agua','categoria':'retro','asset':'pistoladeagua.jpg'},
    {'name':'Star Wars muñeco','categoria':'retro','asset':'starwars.jpg'},
    # vehiculos
    {'name':'Camioneta 4x4','categoria':'vehiculos','asset':'4x4rojo.jpg'},
    {'name':'Auto Volver al Futuro','categoria':'vehiculos','asset':'autovolveralfuturo.jpg'},
    {'name':'Spiderman Involcable','categoria':'vehiculos','asset':'spidermaninvolcable.jpg'},
    {'name':'Spiderman Truck','categoria':'vehiculos','asset':'spidermantruck.jpg'},
]

PRODUCTS = list(Producto.objects.all())

def score(a, b):
    # use difflib ratio on normalized strings
    return difflib.SequenceMatcher(None, normalize(a), normalize(b)).ratio()

def top_candidates(name, topn=5):
    scores = []
    for p in PRODUCTS:
        s = score(name, p.nombre or '')
        scores.append((s, p))
    scores.sort(key=lambda x: -x[0])
    return scores[:topn]

def main():
    for m in MAPPINGS:
        name = m['name']
        print('\nMapping:', name, '->', m['asset'], 'categoria:', m['categoria'])
        cands = top_candidates(name, topn=5)
        for s, p in cands:
            print(f"  ID:{p.id:3d} | score:{s:.3f} | categoria:{p.categoria:10s} | nombre:{p.nombre}")

if __name__ == '__main__':
    main()
