from pathlib import Path
import traceback
from data import storage
from classes.jugador import Jugador
from classes.item import Item
from classes.trap import Trap
from game.engine import GameEngine

def reset_data(base: Path):
    (base/"_data").mkdir(exist_ok=True)
    for fn in ["animals.json","items.json","player.json","traps.json"]:
        p = base/"_data"/fn
        if p.exists(): p.unlink()

def test_spawn_nueva_mascota(base: Path):
    reset_data(base)
    from data.storage import guardar_animales, guardar_items, guardar_trampas
    from classes.gato import Gato
    guardar_animales([Gato(nombre="Michi", especie="gato", energia=50, posicion=(1,0))])
    guardar_items([Item(nombre="Comida+5", tipo="comida", poder=5, posicion=(0,0))])
    guardar_trampas([])

    j = Jugador(nombre="Tester", posicion=(0,0))
    eng = GameEngine(j, remaining_time=30)
    eng.mover_jugador(0,0)  # recoge comida
    prev = len(eng.animales)
    eng.mover_jugador(1,0)  # rescate -> debe spawnear
    assert len(eng.animales) > prev, "Debe haberse spawneado una nueva mascota"

def test_trampas_vida_y_pit(base: Path):
    reset_data(base)
    from data.storage import guardar_animales, guardar_items, guardar_trampas
    guardar_animales([]); guardar_items([])
    guardar_trampas([Trap(nombre="Spike", tipo="spike", daño=1, posicion=(0,0)),
                     Trap(nombre="Pit",   tipo="pit",   daño=-1, posicion=(1,0))])
    j = Jugador(nombre="Tester", posicion=(0,0))
    eng = GameEngine(j, remaining_time=30)
    eng.mover_jugador(0,0); assert j.vidas == 2
    eng.mover_jugador(1,0); assert eng.game_over or j.vidas == 0

def test_tiempo_game_over(base: Path):
    reset_data(base)
    from data.storage import guardar_animales, guardar_items, guardar_trampas
    guardar_animales([]); guardar_items([]); guardar_trampas([])
    j = Jugador(nombre="Tester", posicion=(0,0))
    eng = GameEngine(j, remaining_time=2)
    eng.tick(1); assert eng.remaining_time==1 and not eng.game_over
    eng.tick(1); assert eng.remaining_time==0 and eng.game_over

def run():
    base = Path(__file__).resolve().parents[1]
    tests = [test_spawn_nueva_mascota, test_trampas_vida_y_pit, test_tiempo_game_over]
    for t in tests:
        try:
            t(base); print(f"✔ {t.__name__} OK")
        except AssertionError as e:
            print(f"✘ {t.__name__} FAIL: {e}"); raise
        except Exception as e:
            print(f"✘ {t.__name__} ERROR: {e}"); traceback.print_exc(); raise
    print("✔ Selftests OK")

if __name__=="__main__":
    run()
