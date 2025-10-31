import json, re
from pathlib import Path
from typing import List, Tuple
from classes.perro import Perro
from classes.gato import Gato
from classes.animal import Animal
from classes.item import Item
from classes.trap import Trap

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "_data"
DATA.mkdir(exist_ok=True)

ANIMALS_JSON = DATA / "animals.json"
ITEMS_JSON   = DATA / "items.json"
TRAPS_JSON   = DATA / "traps.json"
PLAYER_JSON  = DATA / "player.json"

def _validar_nombre(n:str) -> bool:
    return bool(re.fullmatch(r"[A-Za-zÁÉÍÓÚÑáéíóúñ\s]{2,30}", n))

# ---------- ANIMALES ----------
def cargar_animales() -> List[Animal]:
    if not ANIMALS_JSON.exists(): return []
    data = json.loads(ANIMALS_JSON.read_text(encoding="utf-8"))
    res: List[Animal] = []
    for a in data:
        cls = Perro if a["especie"] == "perro" else Gato
        obj = cls(nombre=a["nombre"], especie=a["especie"], energia=a["energia"],
                  posicion=tuple(a["posicion"]), rescatado=a.get("rescatado", False))
        obj.nivel = a.get("nivel", 1)
        res.append(obj)
    return res

def guardar_animales(animales: List[Animal]) -> None:
    ANIMALS_JSON.write_text(json.dumps([a.to_dict() for a in animales], ensure_ascii=False, indent=2), encoding="utf-8")

def crear_animal(nombre:str, especie:str, energia:int, nivel:int, pos:Tuple[int,int]) -> Animal:
    if especie not in {"perro","gato"}: raise ValueError("Especie inválida")
    if not _validar_nombre(nombre): raise ValueError("Nombre inválido (2-30, solo letras/espacios)")
    cls = Perro if especie == "perro" else Gato
    a = cls(nombre=nombre, especie=especie, energia=energia, posicion=pos)
    a.nivel = nivel
    data = cargar_animales()
    data.append(a)
    guardar_animales(data)
    return a

def leer_animal(nombre:str) -> Animal|None:
    for a in cargar_animales():
        if a.nombre.lower()==nombre.lower(): return a
    return None

def actualizar_animal(nombre:str, **campos) -> bool:
    data = cargar_animales()
    ok = False
    for a in data:
        if a.nombre.lower()==nombre.lower():
            if "energia" in campos: a.energia = int(campos["energia"])
            if "nivel"   in campos: a.nivel   = int(campos["nivel"])
            if "posicion" in campos: a.posicion = tuple(campos["posicion"])
            if "rescatado" in campos: a.rescatado = bool(campos["rescatado"])
            ok = True; break
    if ok: guardar_animales(data)
    return ok

def borrar_animal(nombre:str) -> bool:
    data = cargar_animales()
    new = [a for a in data if a.nombre.lower()!=nombre.lower()]
    if len(new)==len(data): return False
    guardar_animales(new); return True

# ---------- ITEMS ----------
def cargar_items() -> List[Item]:
    if not ITEMS_JSON.exists(): return []
    data = json.loads(ITEMS_JSON.read_text(encoding="utf-8"))
    return [Item(**{**i, "posicion": tuple(i["posicion"])}) for i in data]

def guardar_items(items: List[Item]) -> None:
    ITEMS_JSON.write_text(json.dumps([i.to_dict() for i in items], ensure_ascii=False, indent=2), encoding="utf-8")

# ---------- TRAPS ----------
def cargar_trampas() -> List[Trap]:
    if not TRAPS_JSON.exists(): return []
    data = json.loads(TRAPS_JSON.read_text(encoding="utf-8"))
    traps: List[Trap] = []
    for t in data:
        traps.append(Trap(
            nombre=t["nombre"], tipo=t["tipo"], daño=t["daño"],
            posicion=tuple(t["posicion"]), visible=t.get("visible",True),
            activo=t.get("activo",True), dx=t.get("dx",0), dy=t.get("dy",0)))
    return traps

def guardar_trampas(traps: List[Trap]) -> None:
    TRAPS_JSON.write_text(json.dumps([t.to_dict() for t in traps], ensure_ascii=False, indent=2), encoding="utf-8")

# ---------- PLAYER ----------
def guardar_player(nombre: str) -> None:
    PLAYER_JSON.write_text(json.dumps({"nombre": nombre}, ensure_ascii=False, indent=2), encoding="utf-8")
