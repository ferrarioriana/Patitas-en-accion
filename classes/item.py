from dataclasses import dataclass
from typing import Tuple

@dataclass
class Item:
    """
    tipo:
      - comida (alimenta mascota)
      - juguete (puntos)
      - detector (revela camo)
      - escudo   (absorbe 1 golpe)
    """
    nombre: str
    tipo: str
    poder: int
    posicion: Tuple[int, int]

    def to_dict(self) -> dict:
        return {
            "nombre": self.nombre,
            "tipo": self.tipo,
            "poder": self.poder,
            "posicion": list(self.posicion),
        }
