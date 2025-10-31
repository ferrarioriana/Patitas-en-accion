from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class Animal(ABC):
    """Base de mascotas a rescatar."""
    nombre: str
    especie: str          # "perro" | "gato"
    energia: int          # 0..100
    posicion: Tuple[int, int]
    rescatado: bool = False
    __nivel: int = field(default=1, repr=False)  # encapsulado

    @property
    def nivel(self) -> int:
        return self.__nivel

    @nivel.setter
    def nivel(self, val: int) -> None:
        if not 1 <= val <= 10:
            raise ValueError("El nivel debe estar entre 1 y 10")
        self.__nivel = val

    @abstractmethod
    def sonido(self) -> str: ...

    def gastar_energia(self, n: int = 1) -> None:
        self.energia = max(0, self.energia - max(0, n))

    def recuperar_energia(self, n: int = 5) -> None:
        self.energia = min(100, self.energia + max(0, n))

    def is_dead(self) -> bool:
        return self.energia <= 0

    def to_dict(self) -> dict:
        return {
            "nombre": self.nombre,
            "especie": self.especie,
            "energia": self.energia,
            "nivel": self.__nivel,
            "posicion": list(self.posicion),
            "rescatado": self.rescatado,
        }

