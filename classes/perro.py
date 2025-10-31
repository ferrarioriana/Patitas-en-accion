from dataclasses import dataclass
from .animal import Animal

@dataclass
class Perro(Animal):
    def sonido(self) -> str:
        return "Guau!"
