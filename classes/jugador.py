from dataclasses import dataclass, field
from typing import List, Tuple
from collections import deque

@dataclass
class Jugador:
    nombre: str
    posicion: Tuple[int, int] = (0, 0)
    inventario: List[str] = field(default_factory=list)
    _Jugador__puntuacion: int = field(default=0, repr=False)
    historial_eventos: deque = field(default_factory=lambda: deque(maxlen=80))
    __vidas: int = field(default=3, repr=False)
    invulnerable_ticks: int = field(default=0, repr=False)
    poison_ticks: int = field(default=0, repr=False)
    escudos: int = field(default=0, repr=False)

    @property
    def puntuacion(self) -> int:
        return self.__puntuacion

    @property
    def vidas(self) -> int:
        return self.__vidas

    def sumar_puntos(self, pts: int) -> None:
        self.__puntuacion += max(0, pts)

    def perder_vida(self, dmg: int = 1) -> None:
        if self.invulnerable_ticks > 0:
            return
        if self.escudos > 0:
            self.escudos -= 1
            self.log("¡Escudo absorbió el daño!")
            self.invulnerable_ticks = 2
            return
        self.__vidas = max(0, self.__vidas - max(0, dmg))
        self.invulnerable_ticks = 2
        self.log(f"Perdiste {dmg} vida(s). Vidas: {self.__vidas}")

    def curar_vida(self, q: int = 1) -> None:
        self.__vidas += max(0, q)
        self.log(f"Recuperaste {q} vida(s). Vidas: {self.__vidas}")

    def tick_estado(self) -> None:
        if self.invulnerable_ticks > 0:
            self.invulnerable_ticks -= 1
        if self.poison_ticks > 0:
            self.poison_ticks -= 1
            self.perder_vida(1)
            self.log("Veneno -1")

    def mover(self, dx: int, dy: int) -> None:
        x, y = self.posicion
        self.posicion = (x + dx, y + dy)

    def log(self, msg: str) -> None:
        self.historial_eventos.append(msg)
