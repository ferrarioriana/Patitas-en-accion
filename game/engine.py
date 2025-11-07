import random
from typing import List, Optional, Set, Tuple
from classes.jugador import Jugador
from classes.animal import Animal
from classes.item import Item
from classes.trap import Trap
from classes.perro import Perro
from classes.gato import Gato
from data import storage

MAP_W, MAP_H = 10, 10
MIN_FOOD_TILES = 4
PET_RESPAWN_DELAY = 1.0
MONSTER_HIT_MSG = "El monstruo te atrapó"

NOMBRES_MASCOTAS = ["Kira", "Chispa", "Rolo", "Lili", "Nora", "Bowie", "Rita", "Max"]


class GameEngine:
    def __init__(self, jugador: Jugador, max_animales_muertos: int = 3, remaining_time: int = 120):
        self.jugador = jugador
        self.animales: List[Animal] = storage.cargar_animales()
        self.items: List[Item] = storage.cargar_items()
        self.trampas: List[Trap] = storage.cargar_trampas()
        self.game_over = False
        self.max_animales_muertos = max_animales_muertos
        self.remaining_time = remaining_time

        self.path_cells: Set[Tuple[int, int]] = set()
        self.tree_cells: Set[Tuple[int, int]] = set()
        self.flower_cells: Set[Tuple[int, int]] = set()
        self.first_move_done = False

        self.monster_active = False
        self.monster_pos: Optional[Tuple[int, int]] = None

        self._pet_respawn_delay: Optional[float] = None

        self._normalize_animales()
        self._init_decor()
        self._ensure_food_tiles()
        if not self._active_animals():
            self._spawn_nueva_mascota(force=True)

    # --------------------------------------------------------------------- #
    # Inicialización / utilidades
    # --------------------------------------------------------------------- #
    def _init_decor(self) -> None:
        """Genera caminos, árboles y flores manteniendo la estética original."""
        cx = MAP_W // 2
        self.path_cells = {(cx, y) for y in range(MAP_H)}
        for y in range(2, MAP_H, 4):
            self.path_cells.add((min(MAP_W - 1, cx + 1), y))
        for y in range(4, MAP_H, 6):
            self.path_cells.add((max(0, cx - 1), y))

        ocupadas = {self.jugador.posicion}
        ocupadas |= {i.posicion for i in self.items}
        ocupadas |= {t.posicion for t in self.trampas}
        ocupadas |= {a.posicion for a in self._active_animals()}

        libres = [
            (x, y)
            for x in range(MAP_W)
            for y in range(MAP_H)
            if (x, y) not in self.path_cells and (x, y) not in ocupadas
        ]
        random.shuffle(libres)
        self.tree_cells = set(libres[:10])
        self.flower_cells = set(libres[10:18])

    def _normalize_animales(self) -> None:
        """Asegura que solo haya una mascota activa a la vez."""
        activos = [idx for idx, a in enumerate(self.animales) if not a.rescatado and not a.is_dead()]
        if len(activos) <= 1:
            return
        changed = False
        for idx in activos[1:]:
            self.animales[idx].rescatado = True
            changed = True
        if changed:
            storage.guardar_animales(self.animales)
            self.animales = storage.cargar_animales()

    def _active_animals(self) -> List[Animal]:
        return [a for a in self.animales if not a.rescatado and not a.is_dead()]

    def _blocked_cells(self) -> Set[Tuple[int, int]]:
        blocked = set(self.tree_cells)
        blocked |= {self.jugador.posicion}
        blocked |= {i.posicion for i in self.items}
        blocked |= {t.posicion for t in self.trampas if t.activo}
        blocked |= {a.posicion for a in self._active_animals()}
        if self.monster_pos:
            blocked.add(self.monster_pos)
        return blocked

    def _random_free_cell(self, extra_blocked: Optional[Set[Tuple[int, int]]] = None) -> Optional[Tuple[int, int]]:
        blocked = self._blocked_cells()
        if extra_blocked:
            blocked |= extra_blocked
        libres = [(x, y) for x in range(MAP_W) for y in range(MAP_H) if (x, y) not in blocked]
        return random.choice(libres) if libres else None

    def _ensure_food_tiles(self) -> None:
        food = [i for i in self.items if i.tipo == "comida"]
        created = False
        while len(food) < MIN_FOOD_TILES:
            pos = self._random_free_cell()
            if pos is None:
                break
            poder = random.randint(3, 8)
            item = Item(nombre=f"Comida+{poder}", tipo="comida", poder=poder, posicion=pos)
            self.items.append(item)
            food.append(item)
            created = True
        if created:
            storage.guardar_items(self.items)

    def _consume_comida(self) -> Optional[str]:
        for idx, nombre in enumerate(self.jugador.inventario):
            if nombre.lower().startswith("comida"):
                return self.jugador.inventario.pop(idx)
        return None

    # --------------------------------------------------------------------- #
    # Ciclo principal
    # --------------------------------------------------------------------- #
    def tick(self, seconds: int = 1) -> None:
        if self.game_over:
            return
        self.remaining_time = max(0, self.remaining_time - max(0, seconds))
        for t in self.trampas:
            if t.tipo == "moving" and t.activo:
                x, y = t.posicion
                t.posicion = ((x + t.dx) % MAP_W, (y + t.dy) % MAP_H)
        storage.guardar_trampas(self.trampas)
        self.jugador.tick_estado()
        if self._pet_respawn_delay is not None:
            if self._active_animals():
                self._pet_respawn_delay = None
            else:
                self._pet_respawn_delay = max(0.0, self._pet_respawn_delay - seconds)
                if self._pet_respawn_delay == 0:
                    self._pet_respawn_delay = None
                    self._spawn_nueva_mascota()
        if self.remaining_time == 0:
            self._set_game_over("Se acabó el tiempo")

    def mover_jugador(self, dx: int, dy: int) -> Tuple[int, int]:
        if self.game_over:
            return self.jugador.posicion
        x, y = self.jugador.posicion
        nx = min(max(0, x + dx), MAP_W - 1)
        ny = min(max(0, y + dy), MAP_H - 1)
        destino = (nx, ny)
        if destino in self.tree_cells and destino != self.jugador.posicion:
            self.jugador.log("Un árbol bloquea ese camino 🌳")
            return self.jugador.posicion
        moved = destino != self.jugador.posicion
        self.jugador.posicion = destino
        if moved and not self.first_move_done:
            self.first_move_done = True
        self.jugador.log(f"Movido a {self.jugador.posicion}")
        self._check_celda()
        self._evaluar_game_over()
        return self.jugador.posicion

    def _check_celda(self) -> None:
        items_changed = False
        food_picked = False
        for it in list(self.items):
            if it.posicion == self.jugador.posicion:
                if it.tipo == "comida":
                    self.jugador.inventario.append(it.nombre)
                    self.jugador.sumar_puntos(5)
                    food_picked = True
                    self.jugador.log(f"Comida (+5): {it.nombre}")
                elif it.tipo == "escudo":
                    self.jugador.escudos += 1
                    self.jugador.log("¡Escudo!")
                elif it.tipo == "detector":
                    self.jugador.inventario.append("Detector")
                    self.jugador.log("Detector")
                else:
                    self.jugador.sumar_puntos(3)
                    self.jugador.log(f"Juguete (+3): {it.nombre}")
                self.items.remove(it)
                items_changed = True
        if items_changed:
            storage.guardar_items(self.items)
            if food_picked:
                self._ensure_food_tiles()

        trap_triggered = False
        for t in self.trampas:
            if t.activo and t.posicion == self.jugador.posicion:
                self._resolver_trampa(t)
                trap_triggered = True
                break
        if trap_triggered:
            storage.guardar_trampas(self.trampas)

        for a in self._active_animals():
            if a.posicion == self.jugador.posicion:
                comida = self._consume_comida()
                if comida:
                    a.rescatado = True
                    self.jugador.sumar_puntos(20)
                    self.jugador.log(f"Rescataste a {a.nombre} ({a.especie}) (+20)")
                    storage.guardar_animales(self.animales)
                    self.animales = storage.cargar_animales()
                    self._pet_respawn_delay = PET_RESPAWN_DELAY
                else:
                    a.gastar_energia(1)
                    storage.guardar_animales(self.animales)
                    self.animales = storage.cargar_animales()
                    self.jugador.log(f"{a.nombre} '{a.sonido()}' — necesita comida")
                break

        if self.monster_active and self.monster_pos == self.jugador.posicion:
            self._set_game_over(MONSTER_HIT_MSG)

    def _resolver_trampa(self, trap: Trap) -> None:
        self.jugador.invulnerable_ticks = 0
        self.jugador.perder_vida(1)
        if trap.tipo == "poison":
            self.jugador.poison_ticks = max(self.jugador.poison_ticks, trap.daño)
            self.jugador.log(f"Veneno activo por {trap.daño} turnos")
        if trap.tipo != "moving":
            trap.activo = False

    def _spawn_nueva_mascota(self, force: bool = False) -> None:
        if not force and self._active_animals():
            return
        pos = self._random_free_cell()
        if pos is None:
            return
        especie = random.choice(["perro", "gato"])
        nombre = random.choice(NOMBRES_MASCOTAS)
        energia = random.randint(40, 90)
        cls = Perro if especie == "perro" else Gato
        mascota = cls(nombre=nombre, especie=especie, energia=energia, posicion=pos)
        mascota.nivel = random.randint(1, 5)
        self.animales.append(mascota)
        storage.guardar_animales(self.animales)
        self.animales = storage.cargar_animales()
        self.jugador.log(f"Nueva mascota en {pos}")

    # --------------------------------------------------------------------- #
    # Monstruo perseguidor
    # --------------------------------------------------------------------- #
    def spawn_monster(self) -> bool:
        if self.game_over or self.monster_active:
            return False
        pos = self._random_free_cell()
        if pos is None:
            return False
        self.monster_pos = pos
        self.monster_active = True
        self.jugador.log(f"¡Un monstruo apareció en {pos}!")
        if self.monster_pos == self.jugador.posicion:
            self._set_game_over(MONSTER_HIT_MSG)
        return True

    def monster_step(self) -> None:
        if not self.monster_active or self.monster_pos is None or self.game_over:
            return
        mx, my = self.monster_pos
        px, py = self.jugador.posicion
        dx = 1 if px > mx else -1 if px < mx else 0
        dy = 1 if py > my else -1 if py < my else 0
        candidates = []
        if dx != 0:
            candidates.append((mx + dx, my))
        if dy != 0:
            candidates.append((mx, my + dy))
        if dx != 0 and dy != 0:
            candidates.append((mx + dx, my + dy))
        candidates.append((mx, my))
        for cx, cy in candidates:
            if 0 <= cx < MAP_W and 0 <= cy < MAP_H and (cx, cy) not in self.tree_cells:
                self.monster_pos = (cx, cy)
                break
        if self.monster_pos == self.jugador.posicion:
            self._set_game_over(MONSTER_HIT_MSG)

    # --------------------------------------------------------------------- #
    # Game over / CRUD
    # --------------------------------------------------------------------- #
    def _evaluar_game_over(self) -> None:
        muertos = sum(1 for a in self.animales if a.is_dead())
        if muertos >= self.max_animales_muertos:
            self._set_game_over(f"{muertos} animales murieron")
        if self.jugador.vidas <= 0:
            self._set_game_over("Te quedaste sin vidas")

    def _set_game_over(self, motivo: str) -> None:
        if self.game_over:
            return
        self.game_over = True
        self.monster_active = False
        self.jugador.log(f"GAME OVER: {motivo}")

    # CRUD passthrough (manteniendo las nuevas reglas)
    def crear_animal(self, *args, **kwargs):
        a = storage.crear_animal(*args, **kwargs)
        self.animales = storage.cargar_animales()
        self._normalize_animales()
        if not self._active_animals():
            self._spawn_nueva_mascota(force=True)
        return a

    def leer_animal(self, nombre: str):
        return storage.leer_animal(nombre)

    def actualizar_animal(self, nombre: str, **campos):
        pos = campos.get("posicion")
        if pos and tuple(pos) in self.tree_cells:
            raise ValueError("No se puede colocar una mascota sobre un árbol")
        ok = storage.actualizar_animal(nombre, **campos)
        self.animales = storage.cargar_animales()
        self._normalize_animales()
        if not self._active_animals():
            self._spawn_nueva_mascota(force=True)
        return ok

    def borrar_animal(self, nombre: str):
        ok = storage.borrar_animal(nombre)
        self.animales = storage.cargar_animales()
        self._normalize_animales()
        if not self._active_animals():
            self._spawn_nueva_mascota(force=True)
        return ok
