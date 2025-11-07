import math
import random
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from game.engine import GameEngine, MAP_W, MAP_H
from classes.jugador import Jugador

CELL = 56

# Paleta pastel
COL_BG   = "#FFF6E9"  # crema
COL_GRID = "#DCECCB"  # verde suave
COL_PATH = "#F4D9A6"  # sendero
COL_ITEM = "#AEC8FF"  # items
COL_ANIM = "#7BC96F"  # mascotas (fallback)
COL_ANIM_RES = "#BDBDBD"
COL_PLAYER = "#F48FB1"  # jugador
COL_TRAP = "#FFB3BA"    # trampas
COL_TREE_DARK = "#7CB342"
COL_TREE_LIGHT = "#A5D6A7"
COL_TRUNK = "#8D6E63"
COL_FLOWER_PETAL = "#F9B4C4"
COL_FLOWER_CENTER = "#FFD166"
COL_PAW = "#7BC96F"
COL_PAW_ACCENT = "#5C8A57"
COL_SHADOW = "#E7D1B0"

TITLE_FONT = ("Helvetica", 28, "bold")
HUD_FONT   = ("Helvetica", 14)
UI_FONT    = ("Helvetica", 12, "bold")
INV_FONT   = ("Helvetica", 12)  # mismo “family” que el título

# ──────────────────────────────────────────────────────────────────────────────
# Inventario custom (canvas con borde de troncos animados)
# ──────────────────────────────────────────────────────────────────────────────
class InventoryWidget(tk.Canvas):
    def __init__(self, parent, width=320, height=200, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=COL_BG, highlightthickness=0, **kw)
        self.items: list[str] = []
        self.trunk_ids: list[int] = []
        self.text_ids: list[int] = []
        self._phase = 0.0
        self._draw_frame()
        self._draw_items()

    def set_items(self, items: list[str]):
        self.items = list(items)
        self._draw_items()

    def _draw_frame(self):
        self.delete("frame")
        w, h = int(self["width"]), int(self["height"])
        # Fondo
        self.create_rectangle(8, 8, w-8, h-8, fill=COL_BG, outline="", tags=("frame",))
        # Troncos en los bordes
        self.trunk_ids.clear()
        seg = 24
        # superior e inferior
        for x in range(12, w-12, seg):
            self.trunk_ids.append(self.create_rectangle(x, 4, x+18, 14, fill=COL_TRUNK, outline="", tags=("frame","trunk")))
            self.trunk_ids.append(self.create_rectangle(x, h-14, x+18, h-4, fill=COL_TRUNK, outline="", tags=("frame","trunk")))
        # laterales
        for y in range(20, h-20, seg):
            self.trunk_ids.append(self.create_rectangle(4, y, 14, y+18, fill=COL_TRUNK, outline="", tags=("frame","trunk")))
            self.trunk_ids.append(self.create_rectangle(w-14, y, w-4, y+18, fill=COL_TRUNK, outline="", tags=("frame","trunk")))

    def _draw_items(self):
        for tid in self.find_withtag("invtext"): self.delete(tid)
        self.text_ids.clear()
        x0, y0 = 20, 24
        for i, name in enumerate(self.items):
            self.text_ids.append(
                self.create_text(x0, y0 + i*22, anchor="nw", text=f"• {name}",
                                 font=INV_FONT, fill="#5C4033", tags=("invtext",))
            )

    def animate(self):
        self._phase += 0.18
        for i, rid in enumerate(self.trunk_ids):
            dy = int(1 * math.sin(self._phase + i * 0.6))
            self.move(rid, 0, dy)
            if i % 4 == 0:
                self.move(rid, 0, -dy)

# ──────────────────────────────────────────────────────────────────────────────
# App principal
# ──────────────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self, jugador: Jugador):
        super().__init__()
        self.title("Patitas en Aventura 🐾")
        self.configure(bg=COL_BG)
        self.resizable(False, False)
        self.engine = GameEngine(jugador, remaining_time=65)  # 1:05

        # Animación (fase global)
        self._anim_phase = 0.0
        self._monster_spawn_job: int | None = None
        self._monster_move_job: int | None = None
        self._monster_timer_started = False

        # Cargar sprites de animales (PNG con fondo transparente)
        self._load_animal_images()
        self._load_player_assets()
        # asignación de sprite por nombre (para que no cambie al redibujar)
        self._sprite_idx: dict[str, int] = {}

        # --------- ENCABEZADO / HUD ----------
        header = tk.Frame(self, bg=COL_BG)
        header.grid(row=0, column=0, columnspan=2, sticky="we", padx=16, pady=(10,0))
        title = tk.Label(header, text="Patitas en Aventura", bg=COL_BG, fg="#D85A4F", font=TITLE_FONT)
        title.pack(side="left", padx=(0,20))
        self.lbl_pts  = tk.Label(header, bg="#EFEFEF", text="🟡 0", font=HUD_FONT, padx=12, pady=6)
        self.lbl_resc = tk.Label(header, bg="#EFEFEF", text="🐾 Por rescatar: 0", font=HUD_FONT, padx=12, pady=6)
        self.lbl_time = tk.Label(header, bg="#EFEFEF", text="⏱️ 01:05", font=HUD_FONT, padx=12, pady=6)
        self.lbl_life = tk.Label(header, bg="#EFEFEF", text="❤️ Vidas: 3", font=HUD_FONT, padx=12, pady=6)
        for w in [self.lbl_pts, self.lbl_resc, self.lbl_time, self.lbl_life]:
            w.pack(side="left", padx=6)

        # --------- TABLERO ----------
        self.canvas = tk.Canvas(self, width=MAP_W*CELL, height=MAP_H*CELL, bg=COL_BG, highlightthickness=0)
        self.canvas.grid(row=1, column=0, padx=16, pady=12)

        # --------- Lateral ----------
        side = tk.Frame(self, bg=COL_BG); side.grid(row=1, column=1, sticky="n", padx=(0,16))
        tk.Label(side, text="Inventario", bg=COL_BG, font=UI_FONT).grid(row=0, column=0, sticky="w")
        self.inv_box = InventoryWidget(side, width=320, height=200); self.inv_box.grid(row=1, column=0, sticky="nwe", pady=(4,10))
        self.btn_admin = ttk.Button(side, text="Admin (CRUD)", command=self._toggle_crud); self.btn_admin.grid(row=2, column=0, sticky="we")

        # CRUD (oculto)
        self.frm_crud = ttk.LabelFrame(side, text="CRUD Animales"); self.frm_crud.grid(row=3, column=0, sticky="we", pady=8); self.frm_crud.grid_remove()
        ttk.Label(self.frm_crud, text="Nombre").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        ttk.Label(self.frm_crud, text="Especie").grid(row=1, column=0, sticky="e", padx=4, pady=2)
        ttk.Label(self.frm_crud, text="Energía").grid(row=2, column=0, sticky="e", padx=4, pady=2)
        ttk.Label(self.frm_crud, text="Nivel").grid(row=3, column=0, sticky="e", padx=4, pady=2)
        ttk.Label(self.frm_crud, text="Pos x,y").grid(row=4, column=0, sticky="e", padx=4, pady=2)
        self.ent_nom = ttk.Entry(self.frm_crud, width=18); self.ent_esp = ttk.Combobox(self.frm_crud, values=["perro","gato"], width=16, state="readonly")
        self.ent_en = ttk.Entry(self.frm_crud, width=18); self.ent_niv = ttk.Entry(self.frm_crud, width=18); self.ent_pos = ttk.Entry(self.frm_crud, width=18)
        self.ent_nom.grid(row=0,column=1, padx=4, pady=2); self.ent_esp.grid(row=1,column=1, padx=4, pady=2)
        self.ent_en.grid(row=2,column=1, padx=4, pady=2);  self.ent_niv.grid(row=3,column=1, padx=4, pady=2); self.ent_pos.grid(row=4,column=1, padx=4, pady=2)
        btns = ttk.Frame(self.frm_crud); btns.grid(row=5, column=0, columnspan=2, pady=6)
        ttk.Button(btns, text="Crear", command=self._crud_crear).grid(row=0,column=0, padx=4)
        ttk.Button(btns, text="Leer",  command=self._crud_leer).grid(row=0,column=1, padx=4)
        ttk.Button(btns, text="Act.",  command=self._crud_actualizar).grid(row=0,column=2, padx=4)
        ttk.Button(btns, text="Borrar",command=self._crud_borrar).grid(row=0,column=3, padx=4)

        # Decor (sendero + árboles + flores)
        self._build_decor()

        # Dibujo inicial
        self._draw_grid()
        self._draw_world()

        # Controles
        self.bind("<Up>",    lambda e: self._move(0,-1))
        self.bind("<Down>",  lambda e: self._move(0,1))
        self.bind("<Left>",  lambda e: self._move(-1,0))
        self.bind("<Right>", lambda e: self._move(1,0))

        # Loops
        self.after(200, self._refresh_sidebar)
        self._schedule_tick()
        self._schedule_anim()

    # ---------- Carga de imágenes ----------
    def _load_animal_images(self):
        """Carga PNGs desde assets/animals. Sin PIL, tamaños nativos."""
        self.sprites = {"gato": [], "perro": []}
        root = Path(__file__).resolve().parents[1]
        asset_dir = root / "assets" / "animals"
        patterns = {
            "gato": ["cat_orange.png", "cat_gray.png"],
            "perro": ["dog_brown.png", "dog_gold.png"],
        }
        for especie, files in patterns.items():
            for fn in files:
                p = asset_dir / fn
                if p.exists():
                    try:
                        img = tk.PhotoImage(file=str(p))
                        self.sprites[especie].append(img)
                    except Exception as e:
                        print(f"[WARN] No se pudo cargar {p}: {e}")
        # Si no hay imágenes, luego usaremos fallback vectorial.

    def _load_player_assets(self):
        """Carga sprites opcionales del jugador/monstruo."""
        self.player_sprite = None
        self.monster_sprite = None
        root = Path(__file__).resolve().parents[1]
        player_dir = root / "assets" / "player"
        if not player_dir.exists():
            return
        player_png = player_dir / "player.png"
        monster_png = player_dir / "monster.png"
        try:
            if player_png.exists():
                self.player_sprite = tk.PhotoImage(file=str(player_png))
        except Exception as exc:
            print(f"[WARN] No se pudo cargar {player_png}: {exc}")
            self.player_sprite = None
        try:
            if monster_png.exists():
                self.monster_sprite = tk.PhotoImage(file=str(monster_png))
        except Exception as exc:
            print(f"[WARN] No se pudo cargar {monster_png}: {exc}")
            self.monster_sprite = None

    def _sprite_for(self, nombre: str, especie: str):
        """Retorna la PhotoImage asignada a este animal, o None si no hay."""
        if not self.sprites.get(especie):
            return None
        if nombre not in self._sprite_idx:
            self._sprite_idx[nombre] = random.randrange(len(self.sprites[especie]))
        return self.sprites[especie][self._sprite_idx[nombre]]

    def _draw_paw_placeholder(self, cx:int, cy:int):
        """Fallback minimalista en caso de que falten sprites."""
        base_r = 10
        toe_r = 6
        offsets = [(-8, -10), (0, -12), (8, -10), (0, 0)]
        for dx, dy in offsets[:-1]:
            self.canvas.create_oval(
                cx + dx - toe_r, cy + dy - toe_r,
                cx + dx + toe_r, cy + dy + toe_r,
                fill=COL_PAW, outline="", tags=("obj","anim_animal")
            )
        dx, dy = offsets[-1]
        self.canvas.create_oval(
            cx + dx - base_r, cy + dy - base_r,
            cx + dx + base_r, cy + dy + base_r,
            fill=COL_PAW_ACCENT, outline="", tags=("obj","anim_animal")
        )

    # ---------- Decor helpers ----------
    def _build_decor(self):
        """Usa el layout calculado por el engine para mantener coherencia."""
        if self.engine.path_cells:
            self.path_cells = set(self.engine.path_cells)
        else:
            cx = MAP_W // 2
            self.path_cells = {(cx, y) for y in range(MAP_H)}
        if self.engine.tree_cells:
            self.tree_cells = set(self.engine.tree_cells)
        else:
            self.tree_cells = set()
        if self.engine.flower_cells:
            self.flower_cells = set(self.engine.flower_cells)
        else:
            self.flower_cells = set()

    # ---------- Mostrar/Ocultar CRUD ----------
    def _toggle_crud(self):
        if self.frm_crud.winfo_ismapped(): self.frm_crud.grid_remove()
        else: self.frm_crud.grid()

    # ---------- Grid y Mundo ----------
    def _draw_grid(self):
        self.canvas.delete("grid")
        for x in range(MAP_W):
            for y in range(MAP_H):
                fill = COL_PATH if (x,y) in self.path_cells else COL_GRID
                self.canvas.create_rectangle(
                    x*CELL+6, y*CELL+6, (x+1)*CELL-6, (y+1)*CELL-6,
                    outline="#F2E8D5", fill=fill, width=2, tags=("grid",)
                )
        for (x,y) in self.path_cells:
            cx, cy = x*CELL+CELL//2, y*CELL+CELL//2
            self.canvas.create_oval(cx-5, cy-3, cx+5, cy+3, fill="#EBCB9A", outline="", tags=("grid","anim_path"))
        for (x,y) in self.tree_cells:
            ox, oy = x*CELL, y*CELL
            self.canvas.create_oval(ox+10, oy+6, ox+CELL-10, oy+CELL-18, fill=COL_TREE_LIGHT, outline="", tags=("grid","anim_tree"))
            self.canvas.create_oval(ox+14, oy+10, ox+CELL-14, oy+CELL-22, fill=COL_TREE_DARK, outline="", tags=("grid","anim_tree"))
            self.canvas.create_rectangle(ox+CELL//2-4, oy+CELL-22, ox+CELL//2+4, oy+CELL-8, fill=COL_TRUNK, outline="", tags=("grid","anim_tree"))
        for (x,y) in self.flower_cells:
            cx, cy = x*CELL+CELL//2, y*CELL+CELL//2
            r = 8
            for ang in [0, 72, 144, 216, 288]:
                rad = math.radians(ang)
                px = cx + int(12 * math.cos(rad))
                py = cy + int(12 * math.sin(rad))
                self.canvas.create_oval(px-r, py-r, px+r, py+r, fill=COL_FLOWER_PETAL, outline="", tags=("grid","anim_flower"))
            self.canvas.create_oval(cx-6, cy-6, cx+6, cy+6, fill=COL_FLOWER_CENTER, outline="", tags=("grid","anim_flower"))

    def _draw_world(self):
        self.canvas.delete("obj")
        # Items
        for it in self.engine.items:
            x,y = it.posicion
            self.canvas.create_oval(x*CELL+14, y*CELL+14, x*CELL+CELL-14, y*CELL+CELL-14,
                                    fill=COL_ITEM, outline="", tags="obj")
            ch = "🍖" if it.tipo=="comida" else ("🛡" if it.tipo=="escudo" else ("🔎" if it.tipo=="detector" else "⭐"))
            self.canvas.create_text(x*CELL+CELL//2, y*CELL+CELL//2, text=ch, tags=("obj","anim_item"))

        # Trampas
        for t in self.engine.trampas:
            if not t.activo: continue
            vis = (t.tipo!="camo") or ("Detector" in self.engine.jugador.inventario)
            if vis:
                x,y = t.posicion
                self.canvas.create_rectangle(x*CELL+12, y*CELL+12, x*CELL+CELL-12, y*CELL+CELL-12,
                                             outline="", fill=COL_TRAP, tags=("obj","anim_trap"))
                self.canvas.create_text(x*CELL+CELL//2, y*CELL+CELL//2,
                                        text="☠" if t.tipo=="pit" else "✖", tags=("obj","anim_trap"))

        # Mascotas con PNG kawaii (solo la activa)
        for a in self.engine.animales:
            if a.rescatado or a.is_dead():
                continue
            x, y = a.posicion
            cx = x*CELL + CELL//2
            cy = y*CELL + CELL//2
            # sombra suave para dar profundidad
            self.canvas.create_oval(
                cx-14, y*CELL+CELL-14, cx+14, y*CELL+CELL-6,
                fill=COL_SHADOW, outline="", tags=("obj","anim_shadow")
            )
            img = self._sprite_for(a.nombre, "gato" if a.especie == "gato" else "perro")
            if img:
                self.canvas.create_image(cx, cy, image=img, tags=("obj","anim_animal"), anchor="c")
            else:
                self._draw_paw_placeholder(cx, cy)

        # Jugador
        x,y = self.engine.jugador.posicion
        cx, cy = x*CELL + CELL//2, y*CELL + CELL//2
        if self.player_sprite:
            self.canvas.create_image(cx, cy, image=self.player_sprite, tags=("obj","anim_player"), anchor="c")
        else:
            head_r = 12
            body_w = CELL//3
            body_h = CELL//2
            # cabeza
            self.canvas.create_oval(
                cx-head_r, y*CELL+10, cx+head_r, y*CELL+10+head_r*2,
                fill="#5B5F97", outline="", tags=("obj","anim_player")
            )
            # cuerpo
            self.canvas.create_rectangle(
                cx-body_w//2, y*CELL+20, cx+body_w//2, y*CELL+20+body_h,
                fill="#F45D5D", outline="", tags=("obj","anim_player")
            )
            # piernas
            leg_y = y*CELL+20+body_h
            self.canvas.create_rectangle(
                cx-body_w//2, leg_y, cx-body_w//2+6, leg_y+18, fill="#5B5F97", outline="", tags=("obj","anim_player")
            )
            self.canvas.create_rectangle(
                cx+body_w//2-6, leg_y, cx+body_w//2, leg_y+18, fill="#5B5F97", outline="", tags=("obj","anim_player")
            )

        # Monstruo perseguidor
        if self.engine.monster_active and self.engine.monster_pos:
            mx, my = self.engine.monster_pos
            mcx, mcy = mx*CELL + CELL//2, my*CELL + CELL//2
            if self.monster_sprite:
                self.canvas.create_image(mcx, mcy, image=self.monster_sprite, tags=("obj","anim_monster"), anchor="c")
            else:
                self.canvas.create_oval(
                    mcx-18, mcy-18, mcx+18, mcy+18, fill="#6D2E46", outline="", tags=("obj","anim_monster")
                )
                self.canvas.create_text(mcx, mcy, text="👾", tags=("obj","anim_monster"))

    # ---------- Movimiento ----------
    def _move(self, dx:int, dy:int):
        self.engine.mover_jugador(dx, dy)
        if (not self._monster_timer_started and not self.engine.game_over and
                self.engine.first_move_done):
            self._monster_timer_started = True
            self._monster_spawn_job = self.after(5000, self._activate_monster)
        self._draw_world()
        if self.engine.game_over:
            self._handle_game_over()

    def _activate_monster(self):
        self._monster_spawn_job = None
        if self.engine.game_over:
            return
        spawned = self.engine.spawn_monster()
        self._draw_world()
        if spawned and not self.engine.game_over:
            self._monster_move_job = self.after(500, self._monster_step_loop)

    def _monster_step_loop(self):
        if self.engine.game_over or not self.engine.monster_active:
            return
        self.engine.monster_step()
        self._draw_world()
        if self.engine.game_over:
            self._handle_game_over()
            return
        self._monster_move_job = self.after(500, self._monster_step_loop)

    # ---------- Sidebar/HUD ----------
    def _refresh_sidebar(self):
        self.lbl_pts.config(text=f"🟡 {self.engine.jugador.puntuacion}")
        self.lbl_life.config(text=f"❤️ Vidas: {self.engine.jugador.vidas}")
        activos = sum(1 for a in self.engine.animales if not a.rescatado and not a.is_dead())
        self.lbl_resc.config(text=f"🐾 Por rescatar: {activos}")
        self.inv_box.set_items(self.engine.jugador.inventario)
        if self.engine.game_over:
            self._handle_game_over(); return
        self.after(300, self._refresh_sidebar)

    def _handle_game_over(self):
        if getattr(self, "_game_over_shown", False): return
        self._game_over_shown = True
        if self._monster_spawn_job:
            self.after_cancel(self._monster_spawn_job)
            self._monster_spawn_job = None
        if self._monster_move_job:
            self.after_cancel(self._monster_move_job)
            self._monster_move_job = None
        messagebox.showerror("Game Over", "¡Perdiste! 😢")
        self.unbind("<Up>"); self.unbind("<Down>"); self.unbind("<Left>"); self.unbind("<Right>")

    # ---------- Tick / reloj ----------
    def _schedule_tick(self): self.after(1000, self._tick_gui)
    def _tick_gui(self):
        if self.engine.game_over: self._handle_game_over(); return
        self.engine.tick(1)
        t = max(0, self.engine.remaining_time)
        mm, ss = divmod(t, 60)
        self.lbl_time.config(text=f"⏱️ {mm:02d}:{ss:02d}")
        self._draw_world()
        self._schedule_tick()

    # ---------- Animaciones suaves ----------
    def _schedule_anim(self): self.after(120, self._animate)
    def _animate(self):
        if self.engine.game_over: return
        self._anim_phase += 0.25

        # balanceo árboles / flores
        sway = int(1 * math.sin(self._anim_phase))
        for item in self.canvas.find_withtag("anim_tree"):
            self.canvas.move(item, sway, 0)
        petal_dy = int(1 * math.cos(self._anim_phase))
        for item in self.canvas.find_withtag("anim_flower"):
            self.canvas.move(item, 0, petal_dy)

        # latido mascotas / pequeño rebote del jugador
        bounce = int(1 * (1 + math.sin(self._anim_phase)))
        for tag in self.canvas.find_withtag("anim_animal"):
            self.canvas.move(tag, 0, -bounce)
        for tag in self.canvas.find_withtag("anim_player"):
            self.canvas.move(tag, 0, -bounce)
        for tag in self.canvas.find_withtag("anim_monster"):
            self.canvas.move(tag, 0, -max(1, bounce//2))

        # borde de troncos del inventario
        self.inv_box.animate()

        self._schedule_anim()

    # ---------- CRUD ----------
    def _parse_pos(self, s:str) -> tuple[int,int]:
        xs = [p.strip() for p in s.split(",")]
        if len(xs)!=2: raise ValueError("Pos debe ser x,y")
        x,y = int(xs[0]), int(xs[1])
        if not (0<=x<MAP_W and 0<=y<MAP_H): raise ValueError("Pos fuera de mapa")
        return (x,y)

    def _crud_crear(self):
        try:
            self.engine.crear_animal(
                self.ent_nom.get().strip(), self.ent_esp.get().strip(),
                int(self.ent_en.get()), int(self.ent_niv.get()), self._parse_pos(self.ent_pos.get()))
            messagebox.showinfo("OK","Creado"); self._draw_world()
        except Exception as e: messagebox.showerror("Error", str(e))

    def _crud_leer(self):
        a = self.engine.leer_animal(self.ent_nom.get().strip())
        if not a: messagebox.showwarning("Ops","No encontrado"); return
        self.ent_esp.set(a.especie)
        self.ent_en.delete(0,tk.END); self.ent_en.insert(0,str(a.energia))
        self.ent_niv.delete(0,tk.END); self.ent_niv.insert(0,str(a.nivel))
        self.ent_pos.delete(0,tk.END); self.ent_pos.insert(0,f"{a.posicion[0]},{a.posicion[1]}")

    def _crud_actualizar(self):
        try:
            campos={}
            if self.ent_en.get(): campos["energia"]=int(self.ent_en.get())
            if self.ent_niv.get(): campos["nivel"]=int(self.ent_niv.get())
            if self.ent_pos.get(): campos["posicion"]=self._parse_pos(self.ent_pos.get())
            ok = self.engine.actualizar_animal(self.ent_nom.get().strip(), **campos)
            messagebox.showinfo("OK","Actualizado" if ok else "No se encontró"); self._draw_world()
        except Exception as e: messagebox.showerror("Error", str(e))

    def _crud_borrar(self):
        ok = self.engine.borrar_animal(self.ent_nom.get().strip())
        messagebox.showinfo("OK","Eliminado" if ok else "No se encontró"); self._draw_world()
