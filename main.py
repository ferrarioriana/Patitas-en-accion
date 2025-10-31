import sys
from pathlib import Path
from classes.jugador import Jugador
from data.seeds import seed_animales, seed_items, seed_trampas
from data import storage
from data.storage import cargar_animales

def _ensure_seeds() -> None:
    base = Path(__file__).resolve().parent
    data = base / "_data"
    data.mkdir(exist_ok=True)
    if not (data/"animals.json").exists(): seed_animales(n=8)
    if not (data/"items.json").exists():   seed_items(m=10)
    if not (data/"traps.json").exists():   seed_trampas()
    try:
        if len(cargar_animales()) == 0:
            seed_animales(n=8)
    except Exception:
        seed_animales(n=8)

def bootstrap(gui: bool = True) -> None:
    _ensure_seeds()
    if not gui:
        from tests.selftest import run as run_tests
        run_tests(); return

    from gui.app import App
    nombre = "Rubia"
    storage.guardar_player(nombre)
    jugador = Jugador(nombre=nombre, posicion=(0, 0))
    App(jugador).mainloop()

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        bootstrap(gui=False)
    else:
        try:
            bootstrap(gui=True)
        except KeyboardInterrupt:
            print("\nSaliendo…")
            sys.exit(0)
