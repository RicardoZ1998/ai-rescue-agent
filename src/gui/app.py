"""
Interfaz Gráfica de Usuario (GUI) construida exclusivamente con Tkinter nativo.
Incluye Lienzo Canvas animado y Panel de Estadísticas con Tabla Comparativa (Tarjeta 4.3).
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
    Ventana principal de escritorio para el Agente de Rescate con simulación animada,
    panel de estadísticas individuales y tabla comparativa de los 4 algoritmos.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Agente de Rescate con Víctimas en Riesgo - Inteligencia Artificial")
        self.root.geometry("1200x820")
        self.root.minsize(1000, 700)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configurar estilos de tablas y botones
        self.style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"))
        self.style.configure("Treeview", font=("Consolas", 9), rowheight=24)

        # Estado de datos
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
        
        self.victimas_salvadas_anim: Set[str] = set()
        self.victimas_muertas_anim: Set[str] = set()

        self._construir_interfaz()

    def _construir_interfaz(self):
        panel_principal = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ==========================================
        # COLUMNA IZQUIERDA: CONTROLES
        # ==========================================
        col_izquierda = ttk.Frame(panel_principal, width=350, padding=10)
        panel_principal.add(col_izquierda, weight=1)

        self._crear_panel_archivos(col_izquierda)
        self._crear_panel_configuracion(col_izquierda)
        self._crear_panel_resumen_mapa(col_izquierda)

        # ==========================================
        # COLUMNA DERECHA: VISUALIZACIÓN Y RESULTADOS
        # ==========================================
        col_derecha = ttk.Frame(panel_principal, padding=10)
        panel_principal.add(col_derecha, weight=3)

        # Barra de estado superior
        header_visor = ttk.Frame(col_derecha)
        header_visor.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(header_visor, text="Visualización del Entorno de Rescate", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        self.lbl_tick_actual = ttk.Label(header_visor, text="Tick: 0", font=("Consolas", 12, "bold"), foreground="#0066CC")
        self.lbl_tick_actual.pack(side=tk.RIGHT)

        # Canvas con bordes
        self.canvas_frame = ttk.Frame(col_derecha, borderwidth=2, relief=tk.GROOVE)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.canvas = tk.Canvas(self.canvas_frame, bg="#2C3437")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._mostrar_placeholder_canvas()
        self._crear_leyenda_colores(col_derecha)

        # Panel de Estadísticas y Tabla Comparativa
        self._crear_panel_estadisticas_y_tabla(col_derecha)

    def _mostrar_placeholder_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            380, 180,
            text="Cargue el mapa y las víctimas para comenzar la simulación",
            fill="#AAAAAA",
            font=("Helvetica", 13, "italic"),
            tags="placeholder"
        )

    def _crear_leyenda_colores(self, parent: ttk.Frame):
        frame_leyenda = ttk.Frame(parent)
        frame_leyenda.pack(fill=tk.X, pady=(0, 8))

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

        ttk.Label(frame_archivos, text="Archivo de Mapa:", font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
        fila_mapa = ttk.Frame(frame_archivos)
        fila_mapa.pack(fill=tk.X, pady=(2, 6))

        self.btn_mapa = ttk.Button(fila_mapa, text="Examinar...", command=self._examinar_mapa)
        self.btn_mapa.pack(side=tk.LEFT)

        self.lbl_estado_mapa = ttk.Label(fila_mapa, text="  [No cargado]", foreground="red")
        self.lbl_estado_mapa.pack(side=tk.LEFT, padx=5)

        self.lbl_ruta_mapa = ttk.Label(frame_archivos, text="Ningún archivo seleccionado", font=("Helvetica", 8), foreground="#666666")
        self.lbl_ruta_mapa.pack(anchor=tk.W, pady=(0, 8))

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
        fila_botones_anim.pack(fill=tk.X, pady=(2, 6))

        self.btn_pausa = ttk.Button(fila_botones_anim, text="⏸ Pausar", command=self._pausar_animacion, state=tk.DISABLED)
        self.btn_pausa.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        self.btn_reiniciar = ttk.Button(fila_botones_anim, text="🔄 Reiniciar", command=self._reiniciar_animacion, state=tk.DISABLED)
        self.btn_reiniciar.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))

        # Botón para ejecutar la comparación de los 4 algoritmos de una vez
        self.btn_comparar_todos = ttk.Button(
            frame_config,
            text="📊 Comparar los 4 Algoritmos",
            command=self._comparar_todos_los_algoritmos
        )
        self.btn_comparar_todos.pack(fill=tk.X, ipady=3, pady=(4, 0))

    def _crear_panel_resumen_mapa(self, parent: ttk.Frame):
        frame_info = ttk.LabelFrame(parent, text="Información del Mapa", padding=10)
        frame_info.pack(fill=tk.BOTH, expand=True)

        self.lbl_info_mapa = ttk.Label(
            frame_info,
            text="Dimensiones: ---\nPosición Inicio: ---\nTotal Víctimas: ---",
            font=("Consolas", 9)
        )
        self.lbl_info_mapa.pack(anchor=tk.W)

    def _crear_panel_estadisticas_y_tabla(self, parent: ttk.Frame):
        """5. Panel de estadísticas y tabla comparativa exactamente como en el PDF."""
        frame_resultados = ttk.LabelFrame(parent, text="5. Estadísticas de Ejecución y Comparación", padding=10)
        frame_resultados.pack(fill=tk.BOTH, expand=False)

        # Contenedor horizontal: Tarjeta de Resumen Individual (Izquierda) | Tabla Comparativa (Derecha)
        fila_stats = ttk.Frame(frame_resultados)
        fila_stats.pack(fill=tk.BOTH, expand=True)

        # 1. Resumen Individual en formato caja
        frame_caja_resumen = ttk.LabelFrame(fila_stats, text="RESULTADO DE LA SIMULACIÓN", padding=8)
        frame_caja_resumen.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.lbl_resumen_detallado = ttk.Label(
            frame_caja_resumen,
            text=(
                "Víctimas totales    : ---\n"
                "Víctimas rescatadas : ---\n"
                "Víctimas fallecidas : ---\n"
                "Ticks totales       : ---\n"
                "Nodos expandidos    : ---\n"
                "Tiempo de cómputo   : ---"
            ),
            font=("Consolas", 9),
            justify=tk.LEFT
        )
        self.lbl_resumen_detallado.pack(anchor=tk.W)

        # 2. Tabla Comparativa de Algoritmos (Treeview)
        frame_tabla = ttk.LabelFrame(fila_stats, text="COMPARACIÓN DE ALGORITMOS", padding=8)
        frame_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columnas = ("algoritmo", "nodos", "tiempo", "rescatadas", "fallecidas", "ticks")
        self.tree_comparacion = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=5)

        self.tree_comparacion.heading("algoritmo", text="Algoritmo")
        self.tree_comparacion.heading("nodos", text="Nodos")
        self.tree_comparacion.heading("tiempo", text="Tiempo")
        self.tree_comparacion.heading("rescatadas", text="Rescatadas")
        self.tree_comparacion.heading("fallecidas", text="Fallecidas")
        self.tree_comparacion.heading("ticks", text="Ticks")

        self.tree_comparacion.column("algoritmo", width=85, anchor=tk.CENTER)
        self.tree_comparacion.column("nodos", width=80, anchor=tk.E)
        self.tree_comparacion.column("tiempo", width=85, anchor=tk.E)
        self.tree_comparacion.column("rescatadas", width=85, anchor=tk.CENTER)
        self.tree_comparacion.column("fallecidas", width=85, anchor=tk.CENTER)
        self.tree_comparacion.column("ticks", width=65, anchor=tk.CENTER)

        self.tree_comparacion.pack(fill=tk.BOTH, expand=True)

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
        if not self.mapa:
            return

        self.canvas.delete("all")
        ancho_canvas = self.canvas.winfo_width()
        alto_canvas = self.canvas.winfo_height()

        if ancho_canvas < 50 or alto_canvas < 50:
            ancho_canvas = 650
            alto_canvas = 380

        margen = 20
        celda_w = (ancho_canvas - 2 * margen) / self.mapa.columnas
        celda_h = (alto_canvas - 2 * margen) / self.mapa.filas
        tam_celda = max(18, min(celda_w, celda_h, 60))

        offset_x = (ancho_canvas - (tam_celda * self.mapa.columnas)) / 2
        offset_y = (alto_canvas - (tam_celda * self.mapa.filas)) / 2

        if pos_agente is None:
            pos_agente = self.mapa.inicio

        # 1. Muros y Caminos
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

        # 2. Inicio 'S'
        sr, sc = self.mapa.inicio
        sx1 = offset_x + sc * tam_celda
        sy1 = offset_y + sr * tam_celda
        self.canvas.create_text(
            sx1 + tam_celda / 2, sy1 + tam_celda / 2,
            text="S", fill="#7F8C8D", font=("Helvetica", int(tam_celda * 0.4), "bold")
        )

        # 3. Víctimas
        if self.victimas:
            for v in self.victimas.values():
                vx1 = offset_x + v.columna * tam_celda
                vy1 = offset_y + v.fila * tam_celda
                vx2 = vx1 + tam_celda
                vy2 = vy1 + tam_celda

                ticks_restantes = v.ticks_supervivencia - tick_actual

                if v.id in self.victimas_salvadas_anim:
                    color_fondo = "#27AE60"
                    texto_estado = f"{v.id}\n✓ SALVADA"
                elif v.id in self.victimas_muertas_anim or ticks_restantes < 0:
                    color_fondo = "#E74C3C"
                    texto_estado = f"{v.id}\n✗ MUERTA"
                else:
                    color_fondo = "#F39C12"
                    texto_estado = f"{v.id}\n⏱ {ticks_restantes}"

                pad = tam_celda * 0.08
                self.canvas.create_oval(vx1 + pad, vy1 + pad, vx2 - pad, vy2 - pad, fill=color_fondo, outline="#FFFFFF", width=2)
                self.canvas.create_text(
                    vx1 + tam_celda / 2, vy1 + tam_celda / 2,
                    text=texto_estado, fill="#FFFFFF",
                    font=("Helvetica", max(7, int(tam_celda * 0.22)), "bold"),
                    justify=tk.CENTER
                )

        # 4. Agente
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
        if not self.mapa:
            messagebox.showwarning("Falta Mapa", "Por favor cargue un archivo de mapa válido primero.")
            return
        if not self.victimas:
            messagebox.showwarning("Faltan Víctimas", "Por favor cargue un archivo de víctimas válido primero.")
            return

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

        # Actualizar panel de resumen individual
        self._actualizar_panel_resumen_individual(resultado)

        # Agregar o actualizar la fila de este algoritmo en la tabla comparativa
        self._actualizar_fila_tabla(resultado)

        # Preparar y lanzar animación
        self.paso_actual = 0
        self.animacion_activa = True
        self.animacion_pausada = False
        self.victimas_salvadas_anim.clear()
        self.victimas_muertas_anim.clear()

        self.btn_pausa.config(state=tk.NORMAL, text="⏸ Pausar")
        self.btn_reiniciar.config(state=tk.NORMAL)
        self.btn_iniciar.config(state=tk.DISABLED)

        self._siguiente_paso_animacion()

    def _siguiente_paso_animacion(self):
        if not self.animacion_activa or self.animacion_pausada:
            return

        if not self.resultado_actual or not self.resultado_actual.camino:
            return

        camino = self.resultado_actual.camino
        if self.paso_actual < len(camino):
            accion, r, c = camino[self.paso_actual]
            tick = self.paso_actual
            self.lbl_tick_actual.config(text=f"Tick: {tick} ({accion if accion else 'Inicio'})")

            for v in self.victimas.values():
                if v.id in self.victimas_salvadas_anim:
                    continue
                if v.fila == r and v.columna == c:
                    if tick <= v.ticks_supervivencia:
                        self.victimas_salvadas_anim.add(v.id)
                else:
                    if tick > v.ticks_supervivencia:
                        self.victimas_muertas_anim.add(v.id)

            self._dibujar_mapa_estatico(pos_agente=(r, c), tick_actual=tick)

            self.paso_actual += 1
            delay = int(self.scale_velocidad.get())
            self.after_id = self.root.after(delay, self._siguiente_paso_animacion)
        else:
            self.animacion_activa = False
            self.btn_iniciar.config(state=tk.NORMAL)
            self.btn_pausa.config(state=tk.DISABLED)

    def _actualizar_panel_resumen_individual(self, res: ResultadoBusqueda):
        """Actualiza la caja de resumen individual con el formato del PDF."""
        texto = (
            f"Víctimas totales    : {res.victimas_totales}\n"
            f"Víctimas rescatadas : {res.rescatadas}  (✓)\n"
            f"Víctimas fallecidas : {res.fallecidas}  (✗)\n"
            f"Ticks totales       : {res.ticks_totales}\n"
            f"Nodos expandidos    : {res.nodos_expandidos}\n"
            f"Tiempo de cómputo   : {res.tiempo_segundos:.4f}s"
        )
        self.lbl_resumen_detallado.config(text=texto)

    def _actualizar_fila_tabla(self, res: ResultadoBusqueda):
        """Inserta o actualiza la fila de un algoritmo en la tabla comparativa."""
        # Verificar si ya existe en la tabla para actualizarlo
        for item in self.tree_comparacion.get_children():
            if self.tree_comparacion.item(item, "values")[0] == res.algoritmo:
                self.tree_comparacion.delete(item)

        valores = (
            res.algoritmo,
            str(res.nodos_expandidos),
            f"{res.tiempo_segundos:.4f}s",
            str(res.rescatadas),
            str(res.fallecidas),
            str(res.ticks_totales)
        )
        self.tree_comparacion.insert("", tk.END, values=valores)

    def _comparar_todos_los_algoritmos(self):
        """Ejecuta los 4 algoritmos secuencialmente y llena la tabla completa."""
        if not self.mapa or not self.victimas:
            messagebox.showwarning("Datos Requeridos", "Debe cargar el mapa y las víctimas antes de comparar.")
            return

        # Limpiar tabla
        for item in self.tree_comparacion.get_children():
            self.tree_comparacion.delete(item)

        # Ejecutar los 4 algoritmos
        algoritmos_funcs = [
            busqueda_amplitud,
            busqueda_costo_uniforme,
            lambda m, v: busqueda_profundidad_iterativa(m, v, limite_maximo_cota=16),
            busqueda_a_estrella
        ]

        for func in algoritmos_funcs:
            resultado = func(self.mapa, self.victimas)
            self._actualizar_fila_tabla(resultado)

        messagebox.showinfo(
            "Comparación Exitosa",
            "Los 4 algoritmos fueron ejecutados y comparados con éxito en la tabla inferior."
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
