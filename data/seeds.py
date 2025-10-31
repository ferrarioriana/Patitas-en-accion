import random
from typing import List, Tuple, Set
from classes.perro import Perro
from classes.gato import Gato
from classes.item import Item
from classes.trap import Trap
from data.storage import guardar_animales, guardar_items, guardar_trampas

def _rand_pos(w:int=10, h:int=10, ocupadas: Set[Tuple[int,int]]|None=None) -> Tuple[int,int]:
    libres = [(x,y) for x in range(w) for y in range(h)]
    if ocupadas:
        libres = [p for p in libres if p not in ocupadas]
    return random.choice(libres) if libres else (0,0)

NOMBRES_PERROS = ["Luna","Rocky","Toby","Milo","Lola","Bowie","Nina"]
NOMBRES_GATOS  = ["Michi","Simba","Olivia","Tom","Kira","Lili","Nora"]

def seed_animales(n:int=8, w:int=10, h:int=10) -> None:
    animales: List[Perro|Gato] = []
    ocupadas: Set[Tuple[int,int]] = set()
    for _ in range(n):
        especie = "perro" if random.random()<0.5 else "gato"
        if especie == "perro":
            a = Perro(nombre=random.choice(NOMBRES_PERROS), especie="perro",
                      energia=random.randint(60,100), posicion=_rand_pos(w,h,ocupadas))
        else:
            a = Gato(nombre=random.choice(NOMBRES_GATOS),  especie="gato",
                     energia=random.randint(60,100), posicion=_rand_pos(w,h,ocupadas))
        a.nivel = random.randint(1,5)
        animales.append(a); ocupadas.add(a.posicion)
    guardar_animales(animales)

def seed_items(m:int=10, w:int=10, h:int=10) -> None:
    items: List[Item] = []
    ocupadas: Set[Tuple[int,int]] = set()
    for _ in range(m):
        tipo = random.choice(["comida","juguete"])
        poder = random.randint(3,10)
        pos = _rand_pos(w,h,ocupadas); ocupadas.add(pos)
        items.append(Item(nombre=f"{tipo.title()}+{poder}", tipo=tipo, poder=poder, posicion=pos))
    for extra in [("Detector","detector",1), ("Escudo","escudo",1)]:
        pos = _rand_pos(w,h,ocupadas); ocupadas.add(pos)
        items.append(Item(nombre=extra[0], tipo=extra[1], poder=extra[2], posicion=pos))
    guardar_items(items)

def seed_trampas(w:int=10, h:int=10) -> None:
    traps: List[Trap] = []
    ocupadas: Set[Tuple[int,int]] = set()
    data = [
        ("Spike-1","spike",1),
        ("Spike-2","spike",1),
        ("Pit-1","pit",-1),
        ("Poison-1","poison",4),
        ("Camo-1","camo",1),
        ("Mover-1","moving",1),
    ]
    for nombre, tipo, daño in data:
        pos = _rand_pos(w,h,ocupadas); ocupadas.add(pos)
        dx, dy = (1,0) if tipo=="moving" else (0,0)
        traps.append(Trap(nombre=nombre, tipo=tipo, daño=daño, posicion=pos, visible=(tipo!="camo"), dx=dx, dy=dy))
    guardar_trampas(traps)
