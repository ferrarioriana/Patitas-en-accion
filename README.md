# Patitas en Aventura 🐾

Videojuego educativo desarrollado en Python para la cátedra **Programación III (Facultad de Ingeniería Informática, Prof. Natalia S. Cerdá)**. El objetivo es rescatar mascotas explorando un parque pastel, evitando trampas y administrando inventario, mientras un monstruo persigue al jugador.

El proyecto fue pensado para mostrar buenas prácticas de programación en Python: código modularizado, clases con herencia y encapsulamiento, uso de colecciones estándar (`deque`), persistencia en JSON y una interfaz gráfica hecha con Tkinter.

---

## Requisitos de la consigna y cómo se cumplen

| Ítem | Estado | Evidencia |
| ---- | ------ | --------- |
| **1. Clases y herencia** | ✅ | `classes/animal.py` define la clase abstracta `Animal` (con `@abstractmethod`). Las clases `Perro` y `Gato` en `classes/perro.py` y `classes/gato.py` heredan de `Animal`. La clase principal del juego es `Jugador` (`classes/jugador.py`; atributos `nombre`, `posicion`, `inventario`, `_Jugador__puntuacion`, `__vidas`, etc. con encapsulamiento de `__vidas`). |
| **2. Módulos vistos en clase** | ✅ | Uso de `collections.deque` (historial del jugador), `json` (persistencia en `_data/*.json`), `random` (generación de eventos y spawns) y `re` (validación de nombres). |
| **3. CRUD completo de la clase principal** | ✅ | En `gui/app.py` hay un panel CRUD que usa los métodos `crear_animal`, `leer_animal`, `actualizar_animal`, `borrar_animal` del `GameEngine` (que a su vez delega en `data/storage.py`). |
| **4. Interfaz gráfica** | ✅ | `gui/app.py` implementa la GUI con Tkinter: HUD animado, tablero, inventario, panel de administración y lógica de movimiento. |
| **5. Librerías externas** | ✅ | Solo se usa la biblioteca estándar de Python (Tkinter incluido). No hay dependencias externas extra; basta con Python 3.11+ con Tk instalado. |
| **6. Mejora de trabajos previos** | ✅ | Se añadieron sprites kawaii para animales, nuevo sistema de trampas, monstruo perseguidor, árboles con colisión, inventario animado y lógica de comida/inventario. |

---

## Arquitectura del proyecto

```
Patitas en accion/
├── main.py              # Punto de entrada; inicializa datos y lanza GUI o self-test.
├── classes/             # Lógica orientada a objetos (Animal, Perro, Gato, Item, Jugador, Trap).
├── data/                # Persistencia en JSON y seeds iniciales.
├── game/engine.py       # Mecánicas del juego (movimiento, colisiones, trampas, monstruo, CRUD).
├── gui/app.py           # Interfaz gráfica Tkinter + animaciones.
├── assets/animals/      # Sprites PNG (perros y gatos).
└── tests/selftest.py    # Batería básica de pruebas automáticas.
```

### Clases principales
- **Animal (abstracta)**: Base para mascotas, controla energía/nivel y expone `sonido()`.
- **Perro / Gato**: Implementan los sonidos y heredan comportamiento común.
- **Jugador**: Maneja vidas, inventario (`deque` para historial), posiciones y estado (veneno, escudos).
- **Item**: Representa comida, escudos, etc.
- **Trap**: Define trampas estáticas y móviles.

### Motor de juego (`game/engine.py`)
Se encarga de:
- Mover al jugador respetando obstáculos (árboles).
- Detectar colisiones con trampas, ítems y mascotas (solo una activa a la vez).
- Gestionar el respawn de mascotas y la aparición del monstruo perseguidor.
- Persistir cambios (CRUD) en `_data/*.json`.

### Interfaz (`gui/app.py`)
Responsable de:
- Pintar el tablero pastel (senderos, árboles, flores).
- Mostrar sprites reales de cada mascota (PNG con fondo transparente) y animarlos.
- Dibujar al jugador (sprite o figura vectorial) y al monstruo.
- Administrar el inventario animado y el panel CRUD.
- Sincronizarse con el motor mediante timers (`after`).

---

## Requerimientos técnicos

### Versiones / dependencias
- **Python 3.11+** (Tkinter incluido). En macOS/Linux suele venir con la distribución. En Windows puede instalarse desde [python.org](https://www.python.org/downloads/).
- No se requieren paquetes adicionales (`pip install` innecesario).

### Ejecución
1. Crear el entorno (opcional) e instalar Python 3.11.
2. Desde la raíz del proyecto:
   ```bash
   python3 main.py          # Inicia la interfaz gráfica
   python3 main.py --selftest  # Corre los tests automáticos en consola
   ```
3. Los seeds automáticos crean los archivos JSON en `_data/` si no existen.

### Recursos gráficos
Colocar los sprites en:
```
assets/animals/cat_orange.png
assets/animals/cat_gray.png
assets/animals/dog_brown.png
assets/animals/dog_gold.png
```
Opcionalmente, sprites del jugador/monstruo en `assets/player/player.png` y `assets/player/monster.png`.

---

## Buenas prácticas aplicadas
- **Docstrings y comentarios**: Clases y funciones claves documentadas (ej. `InventoryWidget`, `GameEngine`).
- **Modularización**: Código dividido por responsabilidad (clases, engine, GUI, data, tests).
- **Encapsulamiento**: `Jugador` protege su atributo `__vidas` y utiliza propiedades/métodos para manipularlo.
- **Persistencia segura**: `data/storage.py` centraliza todas las escrituras/lecturas JSON, con validaciones (`_validar_nombre` usando `re`).
- **Testing automático**: `tests/selftest.py` comprueba spawn de mascotas, trampas y condición de tiempo.
- **Animaciones y UX**: Inventario con borde animado (`math.sin/cos`), sprites con sombra y latido suave.

---

## Funcionalidades destacadas
- **Rescate de mascotas**: Solo una mascota viva visible; se necesita comida en inventario para rescatarla.
- **Inventario animado**: Visualiza comida, escudos, detectores y objetos especiales.
- **Trampas dinámicas**: Distintos tipos (spike, pit, poison, moving). Cada golpe resta exactamente una vida.
- **Monstruo perseguidor**: Aparece tras 5 segundos del primer movimiento y avanza cada 0.5s; si alcanza al jugador hay Game Over.
- **Obstáculos naturales**: Árboles bloquean movimiento de jugadores, monstruo y mascotas; el motor controla spawn en casillas libres.
- **CRUD completo de animales**: Desde la GUI se pueden crear, leer, actualizar y borrar mascotas guardadas en JSON.

---

## Cómo continuar
- Agregar efectos visuales extra (corazones al rescatar, partículas, sonidos).
- Incluir más tipos de ítems (medicinas, juguetes especiales).
- Guardar rankings de jugadores en `_data/player.json`.
- Extender los tests con escenarios de monstruo y veneno.

¡Listo! Este README resume el proyecto con foco en los aspectos solicitados por la cátedra y demuestra cómo cada punto de la consigna fue abordado dentro del código. Disfrutá salvando a las mascotas 🐶🐱✨
