import random
from typing import List, Tuple
from classes.jugador import Jugador
from classes.animal import Animal
from classes.item import Item
from classes.trap import Trap
from data import storage

MAP_W, MAP_H = 10, 10

class GameEngine:
    def __init__(self, jugador: Jugador, max_animales_muertos:int=3, remaining_time:int=120):
        self.jugador = jugador
        self.animales: List[Animal] = storage.cargar_animales()
        self.items:    List[Item]   = storage.cargar_items()
        self.trampas:  List[Trap]   = storage.cargar_trampas()
        self.game_over = False
        self.max_animales_muertos = max_animales_muertos
        self.remaining_time = remaining_time

    def tick(self, seconds:int=1) -> None:
        if self.game_over: return
        self.remaining_time = max(0, self.remaining_time - max(0, seconds))
        for t in self.trampas:
            if t.tipo == "moving" and t.activo:
                x,y = t.posicion
                t.posicion = ((x + t.dx) % MAP_W, (y + t.dy) % MAP_H)
        storage.guardar_trampas(self.trampas)
        self.jugador.tick_estado()
        if self.remaining_time == 0: self._set_game_over("Se acabó el tiempo")

    def mover_jugador(self, dx:int, dy:int) -> Tuple[int,int]:
        if self.game_over: return self.jugador.posicion
        x,y = self.jugador.posicion
        nx = min(max(0, x+dx), MAP_W-1)
        ny = min(max(0, y+dy), MAP_H-1)
        self.jugador.posicion = (nx, ny)
        self.jugador.log(f"Movido a {self.jugador.posicion}")
        self._check_celda(); self._evaluar_game_over()
        return self.jugador.posicion

    def _check_celda(self) -> None:
        # Ítems
        for it in list(self.items):
            if it.posicion == self.jugador.posicion:
                if it.tipo == "comida":
                    self.jugador.inventario.append(it.nombre); self.jugador.sumar_puntos(5)
                    self.items.remove(it); self.jugador.log(f"Comida (+5): {it.nombre}")
                elif it.tipo == "escudo":
                    self.jugador.escudos += 1; self.items.remove(it); self.jugador.log("¡Escudo!")
                elif it.tipo == "detector":
                    self.jugador.inventario.append("Detector"); self.items.remove(it); self.jugador.log("Detector")
                else:
                    self.jugador.sumar_puntos(3); self.items.remove(it); self.jugador.log(f"Juguete (+3): {it.nombre}")
        if list(self.items) != storage.cargar_items(): storage.guardar_items(self.items)

        # Trampas
        for t in list(self.trampas):
            if not t.activo: continue
            if t.posicion == self.jugador.posicion:
                if t.tipo in {"spike","zone","camo","moving"}:
                    self.jugador.perder_vida(max(1, t.daño))
                elif t.tipo == "pit":
                    self.jugador.perder_vida(self.jugador.vidas)
                elif t.tipo == "poison":
                    self.jugador.poison_ticks = max(self.jugador.poison_ticks, t.daño)
                    self.jugador.log(f"Veneno {t.daño} ticks")
                if t.tipo != "moving": t.activo = False
        storage.guardar_trampas(self.trampas)

        # Mascotas
        for a in self.animales:
            if not a.rescatado and a.posicion == self.jugador.posicion:
                comida = [i for i in self.jugador.inventario if i.lower().startswith("comida")]
                if comida:
                    self.jugador.inventario.remove(comida[0])
                    a.rescatado = True; self.jugador.sumar_puntos(20)
                    self.jugador.log(f"Rescataste a {a.nombre} ({a.especie}) (+20)")
                    storage.actualizar_animal(a.nombre, rescatado=True)
                    self._spawn_nueva_mascota()
                else:
                    a.gastar_energia(1); storage.actualizar_animal(a.nombre, energia=a.energia)
                    self.jugador.log(f"{a.nombre} '{a.sonido()}' — necesita comida")

    def _spawn_nueva_mascota(self) -> None:
        libres = {(x,y) for x in range(MAP_W) for y in range(MAP_H)}
        ocupadas = {a.posicion for a in self.animales} | {i.posicion for i in self.items} | {t.posicion for t in self.trampas} | {self.jugador.posicion}
        libres = list(libres - ocupadas)
        if not libres: return
        pos = random.choice(libres)
        especie = random.choice(["perro","gato"])
        nombre = random.choice(["Kira","Chispa","Rolo","Lili","Nora","Bowie"])
        energia = random.randint(40,90); nivel = random.randint(1,5)
        storage.crear_animal(nombre, especie, energia, nivel, pos)
        self.animales = storage.cargar_animales()
        self.jugador.log(f"Nueva mascota en {pos}")

    def _evaluar_game_over(self) -> None:
        muertos = sum(1 for a in self.animales if a.is_dead())
        if muertos >= self.max_animales_muertos: self._set_game_over(f"{muertos} animales murieron")
        if self.jugador.vidas <= 0: self._set_game_over("Te quedaste sin vidas")

    def _set_game_over(self, motivo:str) -> None:
        self.game_over = True; self.jugador.log(f"GAME OVER: {motivo}")

    # CRUD passthrough
    def crear_animal(self, *args, **kwargs): a = storage.crear_animal(*args, **kwargs); self.animales = storage.cargar_animales(); return a
    def leer_animal(self, nombre:str): return storage.leer_animal(nombre)
    def actualizar_animal(self, nombre:str, **campos): ok = storage.actualizar_animal(nombre, **campos); 
        # noqa
