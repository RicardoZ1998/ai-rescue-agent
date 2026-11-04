"""
Interfaz Gráfica de Usuario (GUI) construida exclusivamente con Tkinter nativo.
Implementa el lienzo Canvas y la animación tick a tick no bloqueante (Tarjeta 4.2).
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, List, Tuple, Set

from src.models import Mapa, Victima
from src.loader import cargar_mapa, cargar_victimas
from src.algorithms.bfs import busqueda_amplitud, ResultadoBusqueda
from src.algorithms.ucs import busqueda_costo_uniforme
from src.algorithms.iddfs import busqueda_profundidad_iterativa
from src.algorithms.astar import busqueda_a_estrella


class AppRescate:
    """
    Ventana principal de escritorio para el Agente de Rescate con simulación animada.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Agente de Rescate con Víctimas en Riesgo - IA")
        self.root.geometry("1150x780")
        self.root.minsize(950, 650)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Estado de datos del problema
        self.ruta_mapa: Optional[str] = None
        self.ruta_victimas: Optional[str] = None
        self.mapa: Optional[Mapa] = None
        self.victimas: Optional[Dict[str, Victima]] = None
        self.resultado_actual: Optional[ResultadoBusqueda] = None

        # Variables de control de la animación
        self.animacion_activa: bool = False
        self.animacion_pausada: bool = False
        self.paso_actual: int = 0
        self.after_id = None
        
        # Historial de estados de víctimas en la simulación
        self.victimas_salvadas_anim: Set[str] = set()
        self.victimas_muertas_anim: Set[str] = set()

        self._construir_interfaz()

    def _construir_interfaz(self):
        panel_principal = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Columna Izquierda: Controles
        col_izquierda = ttk.Frame(panel_principal, width=340, padding=10)
        panel_principal.add(col_izquierda, weight=1)

        self._crear_panel_archivos(col_izquierda)
        self._crear_panel_configuracion(col_izquierda)
        self._crear_panel_resumen(col_izquierda)

        # Columna Derecha: Canvas y Estadísticas
        col_derecha = ttk.Frame(panel_principal, padding=10)
        panel_principal.add(col_derecha, weight=3)

        # Barra superior del visor con información del tick
        header_visor = ttk.Frame(col_derecha)
        header_visor.pack(fill=tk.X, pady=(0, 5))

        lbl_visor = ttk.Label(header_visor, text="Visualización del Entorno de Rescate", font=("Helvetica", 12, "bold"))
        lbl_visor.pack(side=tk.LEFT)

        self.lbl_tick_actual = ttk.Label(header_visor, text="Tick: 0", font=("Consolas", 12, "bold"), foreground="#0066CC")
        self.lbl_tick_actual.pack(side=tk.RIGHT)

        # Canvas con bordes
        self.canvas_frame = ttk.Frame(col_derecha, borderwidth=2, relief=tk.GROOVE)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.canvas = tk.Canvas(self.canvas_frame, bg="#2C3437")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._mostrar_placeholder_canvas()

        # Leyenda de Colores
        self._crear_leyenda_colores(col_derecha)

        # Panel de Resultados
        self.panel_stats_frame = ttk.LabelFrame(col_derecha, text="Panel de Resultados y Comparación", padding=10)
        self.panel_stats_frame.pack(fill=tk.X)

        self.lbl_stats_resumen = ttk.Label(
            self.panel_stats_frame,
            text="Esperando ejecución del rescate...",
            font=("Consolas", 10)
        )
        self.lbl_stats_resumen.pack(anchor=tk.W)

    def _mostrar_placeholder_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            350, 200,
            text="Cargue el mapa y las víctimas para comenzar la simulación",
            fill="#AAAAAA",
            font=("Helvetica", 13, "italic"),
            tags="placeholder"
        )

    def _crear_leyenda_colores(self, parent: ttk.Frame):
        """Muestra la guía visual de colores requerida por el PDF."""
        frame_leyenda = ttk.Frame(parent)
        frame_leyenda.pack(fill=tk.X, pady=(0, 5))

        elementos = [
            ("Muro (#)", "#1F2421", "white"),
            ("Agente (A)", "#3498DB", "white"),
            ("Víctima Viva", "#F39C12", "white"),
            ("Rescatada (Verde)", "#27AE60", "white"),
            ("Fallecida (Rojo)", "#E74C3C", "white")
        ]

        for nombre, color_bg, color_fg in elementos:
            lbl = tk.Label(frame_leyenda, text=f" {nombre} ", bg=color_bg, fg=color_fg, font=("Helvetica", 8, "bold"), relief=tk.RIDGE)
            lbl.pack(side=tk.LEFT, padx=3)

    def _crear_panel_archivos(self, parent: ttk.Frame):
        frame_archivos = ttk.LabelFrame(parent, text="1. Carga de Archivos", padding=10)
        frame_archivos.pack(fill=tk.X, pady=(0, 10))

        # Mapa.txt
        ttk.Label(frame_archivos, text="Archivo de Mapa:", font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
        fila_mapa = ttk.Frame(frame_archivos)
        fila_mapa.pack(fill=tk.X, pady=(2, 6))

        self.btn_mapa = ttk.Button(fila_mapa, text="Examinar...", command=self._examinar_mapa)
        self.btn_mapa.pack(side=tk.LEFT)

        self.lbl_estado_mapa = ttk.Label(fila_mapa, text="  [No cargado]", foreground="red")
        self.lbl_estado_mapa.pack(side=tk.LEFT, padx=5)

        self.lbl_ruta_mapa = ttk.Label(frame_archivos, text="Ningún archivo seleccionado", font=("Helvetica", 8), foreground="#666666")
        self.lbl_ruta_mapa.pack(anchor=tk.W, pady=(0, 8))

        # Victimas.txt
        ttk.Label(frame_archivos, text="Archivo de Víctimas:", font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
        fila_vic = ttk.Frame(frame_archivos)
        fila_vic.pack(fill=tk.X, pady=(2, 6))

        self.btn_victimas = ttk.Button(fila_vic, text="Examinar...", command=self._examinar_victimas)
        self.btn_victimas.pack(side=tk.LEFT)

        self.lbl_estado_vic = ttk.Label(fila_vic, text="  [No cargado]", foreground="red")
        self.lbl_estado_vic.pack(side=tk.LEFT, padx=5)

        self.lbl_ruta_vic = ttk.Label(frame_archivos, text="Ningún archivo seleccionado", font=("Helvetica", 8), foreground="#666666")
        self.lbl_ruta_vic.pack(anchor=tk.W)

    def _crear_panel_configuracion(self, parent: ttk.Frame):
        frame_config = ttk.LabelFrame(parent, text="2. Configuración de Simulación", padding=10)
        frame_config.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_config, text="Seleccionar Algoritmo:", font=("Helvetica", 9, "bold")).pack(anchor=tk.W, pady=(0, 4))
        self.combo_algoritmo = ttk.Combobox(
            frame_config,
            values=["A*", "BFS", "UCS", "IDDFS"],
            state="readonly"
        )
        self.combo_algoritmo.current(0)
        self.combo_algoritmo.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_config, text="Velocidad (ms por tick):", font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
        fila_vel = ttk.Frame(frame_config)
        fila_vel.pack(fill=tk.X, pady=(2, 10))

        self.scale_velocidad = ttk.Scale(fila_vel, from_=50, to=1000, value=300, orient=tk.HORIZONTAL)
        self.scale_velocidad.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.lbl_vel_val = ttk.Label(fila_vel, text="300 ms", width=8, font=("Consolas", 9))
        self.lbl_vel_val.pack(side=tk.RIGHT, padx=5)
        self.scale_velocidad.configure(command=self._actualizar_etiqueta_velocidad)

        # Botones de control
        self.btn_iniciar = ttk.Button(frame_config, text="🚀 Iniciar Rescate", command=self._iniciar_rescate)
        self.btn_iniciar.pack(fill=tk.X, ipady=4, pady=(2, 4))

        fila_botones_anim = ttk.Frame(frame_config)
        fila_botones_anim.pack(fill=tk.X, pady=(2, 0))

        self.btn_pausa = ttk.Button(fila_botones_anim, text="⏸ Pausar", command=self._pausar_animacion, state=tk.DISABLED)
        self.btn_pausa.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        self.btn_reiniciar = ttk.Button(fila_botones_anim, text="🔄 Reiniciar", command=self._reiniciar_animacion, state=tk.DISABLED)
        self.btn_reiniciar.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))

    def _crear_panel_resumen(self, parent: ttk.Frame):
        frame_info = ttk.LabelFrame(parent, text="Información del Mapa", padding=10)
        frame_info.pack(fill=tk.BOTH, expand=True)

        self.lbl_info_mapa = ttk.Label(
            frame_info,
            text="Dimensiones: ---\nPosición Inicio: ---\nTotal Víctimas: ---",
            font=("Consolas", 9)
        )
        self.lbl_info_mapa.pack(anchor=tk.W)

    def _actualizar_etiqueta_velocidad(self, val):
        ms = int(float(val))
        self.lbl_vel_val.config(text=f"{ms} ms")

    def _examinar_mapa(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar mapa.txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialdir=os.path.abspath("data")
        )
        if not ruta:
            return

        try:
            mapa = cargar_mapa(ruta)
            self.mapa = mapa
            self.ruta_mapa = ruta
            self.lbl_ruta_mapa.config(text=os.path.basename(ruta))
            self.lbl_estado_mapa.config(text="  [✓ Correcto]", foreground="#00AA00")
            self._actualizar_info()
            self._dibujar_mapa_estatico()
        except Exception as e:
            self.mapa = None
            self.lbl_estado_mapa.config(text="  [✗ Error]", foreground="red")
            messagebox.showerror("Error en Mapa", str(e))

    def _examinar_victimas(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar victimas.txt",
            filetypes=[("Archivos de texto o CSV", "*.txt *.csv"), ("Todos los archivos", "*.*")],
            initialdir=os.path.abspath("data")
        )
        if not ruta:
            return

        try:
            victimas = cargar_victimas(ruta, mapa=self.mapa)
            self.victimas = victimas
            self.ruta_victimas = ruta
            self.lbl_ruta_vic.config(text=os.path.basename(ruta))
            self.lbl_estado_vic.config(text="  [✓ Correcto]", foreground="#00AA00")
            self._actualizar_info()
            self._dibujar_mapa_estatico()
        except Exception as e:
            self.victimas = None
            self.lbl_estado_vic.config(text="  [✗ Error]", foreground="red")
            messagebox.showerror("Error en Víctimas", str(e))

    def _actualizar_info(self):
        txt_mapa = f"Dimensiones: {self.mapa.filas}x{self.mapa.columnas}\nInicio 'S': {self.mapa.inicio}" if self.mapa else "Dimensiones: ---\nInicio 'S': ---"
        txt_vic = f"\nTotal Víctimas: {len(self.victimas)}" if self.victimas else "\nTotal Víctimas: ---"
        self.lbl_info_mapa.config(text=txt_mapa + txt_vic)

    def _dibujar_mapa_estatico(self, pos_agente: Optional[Tuple[int, int]] = None, tick_actual: int = 0):
        """
        Dibuja el mapa completo en el Canvas con el estado visual en el tick especificado.
        """
        if not self.mapa:
            return

        self.canvas.delete("all")
        ancho_canvas = self.canvas.winfo_width()
        alto_canvas = self.canvas.winfo_height()

        if ancho_canvas < 50 or alto_canvas < 50:
            ancho_canvas = 650
            alto_canvas = 450

        # Dimensiones de cada celda
        margen = 20
        celda_w = (ancho_canvas - 2 * margen) / self.mapa.columnas
        celda_h = (alto_canvas - 2 * margen) / self.mapa.filas
        tam_celda = max(20, min(celda_w, celda_h, 65))

        offset_x = (ancho_canvas - (tam_celda * self.mapa.columnas)) / 2
        offset_y = (alto_canvas - (tam_celda * self.mapa.filas)) / 2

        if pos_agente is None:
            pos_agente = self.mapa.inicio

        # 1. Dibujar celdas base (Muros y Caminos)
        for r in range(self.mapa.filas):
            for c in range(self.mapa.columnas):
                x1 = offset_x + c * tam_celda
                y1 = offset_y + r * tam_celda
                x2 = x1 + tam_celda
                y2 = y1 + tam_celda

                caracter = self.mapa.celdas[r][c]
                if caracter == '#':
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#1F2421", outline="#34495E")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#ECEFF1", outline="#BDC3C7")

        # 2. Dibujar casilla de inicio 'S'
        sr, sc = self.mapa.inicio
        sx1 = offset_x + sc * tam_celda
        sy1 = offset_y + sr * tam_celda
        self.canvas.create_text(
            sx1 + tam_celda / 2, sy1 + tam_celda / 2,
            text="S", fill="#7F8C8D", font=("Helvetica", int(tam_celda * 0.4), "bold")
        )

        # 3. Dibujar Víctimas
        if self.victimas:
            for v in self.victimas.values():
                vx1 = offset_x + v.columna * tam_celda
                vy1 = offset_y + v.fila * tam_celda
                vx2 = vx1 + tam_celda
                vy2 = vy1 + tam_celda

                ticks_restantes = v.ticks_supervivencia - tick_actual

                # Determinación de color del estado de la víctima
                if v.id in self.victimas_salvadas_anim:
                    # Rescatada (Verde)
                    color_fondo = "#27AE60"
                    texto_estado = f"{v.id}\n✓ SALVADA"
                elif v.id in self.victimas_muertas_anim or ticks_restantes < 0:
                    # Fallecida (Rojo)
                    color_fondo = "#E74C3C"
                    texto_estado = f"{v.id}\n✗ MUERTA"
                else:
                    # Viva en riesgo (Naranja) con contador de ticks restantes visible
                    color_fondo = "#F39C12"
                    texto_estado = f"{v.id}\n⏱ {ticks_restantes}"

                # Círculo o rectángulo redondeado de la víctima
                pad = tam_celda * 0.08
                self.canvas.create_oval(vx1 + pad, vy1 + pad, vx2 - pad, vy2 - pad, fill=color_fondo, outline="#FFFFFF", width=2)
                self.canvas.create_text(
                    vx1 + tam_celda / 2, vy1 + tam_celda / 2,
                    text=texto_estado, fill="#FFFFFF",
                    font=("Helvetica", max(7, int(tam_celda * 0.22)), "bold"),
                    justify=tk.CENTER
                )

        # 4. Dibujar Agente de Rescate en su posición actual
        ar, ac = pos_agente
        ax1 = offset_x + ac * tam_celda
        ay1 = offset_y + ar * tam_celda
        ax2 = ax1 + tam_celda
        ay2 = ay1 + tam_celda

        pad_agente = tam_celda * 0.15
        self.canvas.create_rectangle(
            ax1 + pad_agente, ay1 + pad_agente, ax2 - pad_agente, ay2 - pad_agente,
            fill="#2980B9", outline="#F1C40F", width=3
        )
        self.canvas.create_text(
            ax1 + tam_celda / 2, ay1 + tam_celda / 2,
            text="AGENTE", fill="#FFFFFF",
            font=("Helvetica", max(7, int(tam_celda * 0.2)), "bold")
        )

    def _iniciar_rescate(self):
        """Ejecuta el algoritmo y lanza la simulación animada tick a tick."""
        if not self.mapa:
            messagebox.showwarning("Falta Mapa", "Por favor cargue un archivo de mapa válido primero.")
            return
        if not self.victimas:
            messagebox.showwarning("Faltan Víctimas", "Por favor cargue un archivo de víctimas válido primero.")
            return

        # Cancelar cualquier animación previa en curso
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        algoritmo = self.combo_algoritmo.get()

        if algoritmo == "A*":
            resultado = busqueda_a_estrella(self.mapa, self.victimas)
        elif algoritmo == "BFS":
            resultado = busqueda_amplitud(self.mapa, self.victimas)
        elif algoritmo == "UCS":
            resultado = busqueda_costo_uniforme(self.mapa, self.victimas)
        elif algoritmo == "IDDFS":
            resultado = busqueda_profundidad_iterativa(self.mapa, self.victimas, limite_maximo_cota=16)
        else:
            return

        self.resultado_actual = resultado

        # Preparar la animación
        self.paso_actual = 0
        self.animacion_activa = True
        self.animacion_pausada = False
        self.victimas_salvadas_anim.clear()
        self.victimas_muertas_anim.clear()

        self.btn_pausa.config(state=tk.NORMAL, text="⏸ Pausar")
        self.btn_reiniciar.config(state=tk.NORMAL)
        self.btn_iniciar.config(state=tk.DISABLED)

        # Iniciar bucle de animación
        self._siguiente_paso_animacion()

    def _siguiente_paso_animacion(self):
        """Avanza 1 tick de simulación y programa el siguiente con after()."""
        if not self.animacion_activa or self.animacion_pausada:
            return

        if not self.resultado_actual or not self.resultado_actual.camino:
            return

        camino = self.resultado_actual.camino
        if self.paso_actual < len(camino):
            accion, r, c = camino[self.paso_actual]
            tick = self.paso_actual
            self.lbl_tick_actual.config(text=f"Tick: {tick} ({accion if accion else 'Inicio'})")

            # Actualizar estado de las víctimas para este tick
            for v in self.victimas.values():
                if v.id in self.victimas_salvadas_anim:
                    continue
                # Si el agente pisa la celda de la víctima
                if v.fila == r and v.columna == c:
                    if tick <= v.ticks_supervivencia:
                        self.victimas_salvadas_anim.add(v.id)
                else:
                    # Si no llegó a tiempo y sus ticks llegaron a 0
                    if tick > v.ticks_supervivencia:
                        self.victimas_muertas_anim.add(v.id)

            # Dibujar el fotograma actual en el Canvas
            self._dibujar_mapa_estatico(pos_agente=(r, c), tick_actual=tick)

            self.paso_actual += 1
            delay = int(self.scale_velocidad.get())
            self.after_id = self.root.after(delay, self._siguiente_paso_animacion)
        else:
            # Simulación terminada
            self.animacion_activa = False
            self.btn_iniciar.config(state=tk.NORMAL)
            self.btn_pausa.config(state=tk.DISABLED)

            res = self.resultado_actual
            self.lbl_stats_resumen.config(
                text=(
                    f"SIMULACIÓN FINALIZADA | [{res.algoritmo}] Rescatadas: {res.rescatadas}/{res.victimas_totales} | "
                    f"Fallecidas: {res.fallecidas} | Ticks totales: {res.ticks_totales} | "
                    f"Nodos: {res.nodos_expandidos} | Tiempo: {res.tiempo_segundos:.4f}s"
                )
            )

    def _pausar_animacion(self):
        if self.animacion_pausada:
            self.animacion_pausada = False
            self.btn_pausa.config(text="⏸ Pausar")
            self._siguiente_paso_animacion()
        else:
            self.animacion_pausada = True
            self.btn_pausa.config(text="▶ Reanudar")
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None

    def _reiniciar_animacion(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.animacion_activa = False
        self.animacion_pausada = False
        self.paso_actual = 0
        self.victimas_salvadas_anim.clear()
        self.victimas_muertas_anim.clear()

        self.btn_pausa.config(state=tk.DISABLED, text="⏸ Pausar")
        self.btn_reiniciar.config(state=tk.DISABLED)
        self.btn_iniciar.config(state=tk.NORMAL)
        self.lbl_tick_actual.config(text="Tick: 0")

        self._dibujar_mapa_estatico()


def main():
    root = tk.Tk()
    app = AppRescate(root)
    root.mainloop()


if __name__ == "__main__":
    main()
