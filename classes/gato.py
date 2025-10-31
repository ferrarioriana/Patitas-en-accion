from dataclasses import dataclass
from .animal import Animal

@dataclass
class Gato(Animal):
    def sonido(self) -> str:
        return "Miau!"
