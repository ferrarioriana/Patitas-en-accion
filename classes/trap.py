from dataclasses import dataclass
from typing import Tuple

@dataclass
class Trap:
    """
    tipo:
      - spike  : daño directo
      - pit    : muerte instantánea (daño = -1)
      - poison : aplica poison_ticks = daño
      - camo   : invisible sin detector (pero activa igual)
      - moving : se desplaza 1 celda por tick (dx, dy)
      - zone   : casilla dañina (como spike)
    """
    nombre: str
    tipo: str
    daño: int
    posicion: Tuple[int, int]
    visible: bool = True
    activo: bool = True
    dx: int = 0
    dy: int = 0

    def to_dict(self) -> dict:
        return {
            "nombre": self.nombre,
            "tipo": self.tipo,
            "daño": self.daño,
            "posicion": list(self.posicion),
            "visible": self.visible,
            "activo": self.activo,
            "dx": self.dx,
            "dy": self.dy,
        }
