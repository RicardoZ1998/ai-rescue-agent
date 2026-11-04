"""
Interfaz Gráfica de Usuario (GUI) construida exclusivamente con Tkinter nativo (Tarjeta 4.1).
Sin frameworks externos (PyQt, wxPython, etc.).
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict

from src.models import Mapa, Victima
from src.loader import cargar_mapa, cargar_victimas
from src.algorithms.bfs import busqueda_amplitud, ResultadoBusqueda
from src.algorithms.ucs import busqueda_costo_uniforme
from src.algorithms.iddfs import busqueda_profundidad_iterativa
from src.algorithms.astar import busqueda_a_estrella


class AppRescate:
    """
    Ventana principal de escritorio para el Agente de Rescate.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Agente de Rescate con Víctimas en Riesgo - IA")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)

        # Configuración de estilos
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Estado de datos en memoria
        self.ruta_mapa: Optional[str] = None
        self.ruta_victimas: Optional[str] = None
        self.mapa: Optional[Mapa] = None
        self.victimas: Optional[Dict[str, Victima]] = None
        self.resultado_actual: Optional[ResultadoBusqueda] = None

        # Construcción de la interfaz
        self._construir_interfaz()

    def _construir_interfaz(self):
        """Maqueta los paneles principales: Carga, Configuración, Canvas y Estadísticas."""
        # Contenedor principal con dos columnas: Izquierda (Controles) | Derecha (Visualización)
        panel_principal = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ==========================================
        # COLUMNA IZQUIERDA: CONTROLES
        # ==========================================
        col_izquierda = ttk.Frame(panel_principal, width=320, padding=10)
        panel_principal.add(col_izquierda, weight=1)

        # 1. Panel de Carga de Archivos
        self._crear_panel_archivos(col_izquierda)

        # 2. Panel de Configuración de Búsqueda
        self._crear_panel_configuracion(col_izquierda)

        # 3. Panel de Resumen Rápido
        self._crear_panel_resumen(col_izquierda)

        # ==========================================
        # COLUMNA DERECHA: SIMULACIÓN Y RESULTADOS
        # ==========================================
        col_derecha = ttk.Frame(panel_principal, padding=10)
        panel_principal.add(col_derecha, weight=3)

        # Título del visor
        lbl_visor = ttk.Label(col_derecha, text="Visualización del Entorno de Rescate", font=("Helvetica", 12, "bold"))
        lbl_visor.pack(anchor=tk.W, pady=(0, 5))

        # Canvas para la animación del mapa (se completará con animación en la tarjeta 4.2)
        self.canvas_frame = ttk.Frame(col_derecha, borderwidth=2, relief=tk.GROOVE)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.canvas = tk.Canvas(self.canvas_frame, bg="#1E1E1E")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Mensaje placeholder en el Canvas
        self.canvas.create_text(
            350, 200,
            text="Cargue el mapa y las víctimas para comenzar",
            fill="#888888",
            font=("Helvetica", 14, "italic"),
            tags="placeholder"
        )

        # Panel de Estadísticas y Tabla Comparativa (se completará en la tarjeta 4.3)
        self.panel_stats_frame = ttk.LabelFrame(col_derecha, text="Panel de Resultados y Comparación", padding=10)
        self.panel_stats_frame.pack(fill=tk.X)

        self.lbl_stats_resumen = ttk.Label(
            self.panel_stats_frame,
            text="Esperando ejecución del rescate...",
            font=("Consolas", 10)
        )
        self.lbl_stats_resumen.pack(anchor=tk.W)

    def _crear_panel_archivos(self, parent: ttk.Frame):
        """1. Panel de carga de archivos (mapa.txt y victimas.txt)."""
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
        """2. Panel de configuración de algoritmo y velocidad."""
        frame_config = ttk.LabelFrame(parent, text="2. Configuración de Simulación", padding=10)
        frame_config.pack(fill=tk.X, pady=(0, 10))

        # Selector de Algoritmo
        ttk.Label(frame_config, text="Seleccionar Algoritmo:", font=("Helvetica", 9, "bold")).pack(anchor=tk.W, pady=(0, 4))
        self.combo_algoritmo = ttk.Combobox(
            frame_config,
            values=["A*", "BFS", "UCS", "IDDFS"],
            state="readonly"
        )
        self.combo_algoritmo.current(0)  # Por defecto A*
        self.combo_algoritmo.pack(fill=tk.X, pady=(0, 10))

        # Control de velocidad (milisegundos por tick)
        ttk.Label(frame_config, text="Velocidad de Simulación (ms/tick):", font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
        
        fila_vel = ttk.Frame(frame_config)
        fila_vel.pack(fill=tk.X, pady=(2, 10))

        self.scale_velocidad = ttk.Scale(fila_vel, from_=50, to=1000, value=250, orient=tk.HORIZONTAL)
        self.scale_velocidad.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.lbl_vel_val = ttk.Label(fila_vel, text="250 ms", width=8, font=("Consolas", 9))
        self.lbl_vel_val.pack(side=tk.RIGHT, padx=5)
        self.scale_velocidad.configure(command=self._actualizar_etiqueta_velocidad)

        # Botón Iniciar Rescate
        self.btn_iniciar = ttk.Button(
            frame_config,
            text="🚀 Iniciar Rescate",
            command=self._iniciar_rescate
        )
        self.btn_iniciar.pack(fill=tk.X, ipady=5, pady=(5, 0))

    def _crear_panel_resumen(self, parent: ttk.Frame):
        """Panel informativo sobre los datos cargados."""
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
        """Abre cuadro de diálogo para seleccionar mapa.txt y valida."""
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
            messagebox.showinfo("Lectura Exitosa", f"Mapa cargado con éxito:\n{mapa.filas} filas x {mapa.columnas} columnas.\nInicio 'S' en {mapa.inicio}.")
        except Exception as e:
            self.mapa = None
            self.lbl_estado_mapa.config(text="  [✗ Error]", foreground="red")
            messagebox.showerror("Error en Mapa", str(e))

    def _examinar_victimas(self):
        """Abre cuadro de diálogo para seleccionar victimas.txt y valida."""
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
            messagebox.showinfo("Lectura Exitosa", f"Se cargaron {len(victimas)} víctimas correctamente.")
        except Exception as e:
            self.victimas = None
            self.lbl_estado_vic.config(text="  [✗ Error]", foreground="red")
            messagebox.showerror("Error en Víctimas", str(e))

    def _actualizar_info(self):
        """Actualiza el resumen de información del entorno."""
        txt_mapa = f"Dimensiones: {self.mapa.filas}x{self.mapa.columnas}\nInicio 'S': {self.mapa.inicio}" if self.mapa else "Dimensiones: ---\nInicio 'S': ---"
        txt_vic = f"\nTotal Víctimas: {len(self.victimas)}" if self.victimas else "\nTotal Víctimas: ---"
        self.lbl_info_mapa.config(text=txt_mapa + txt_vic)

    def _iniciar_rescate(self):
        """Ejecuta el algoritmo seleccionado y prepara la simulación."""
        if not self.mapa:
            messagebox.showwarning("Falta Mapa", "Por favor cargue un archivo de mapa válido primero.")
            return
        if not self.victimas:
            messagebox.showwarning("Faltan Víctimas", "Por favor cargue un archivo de víctimas válido primero.")
            return

        algoritmo = self.combo_algoritmo.get()

        # Ejecución del algoritmo seleccionado
        if algoritmo == "A*":
            resultado = busqueda_a_estrella(self.mapa, self.victimas)
        elif algoritmo == "BFS":
            resultado = busqueda_amplitud(self.mapa, self.victimas)
        elif algoritmo == "UCS":
            resultado = busqueda_costo_uniforme(self.mapa, self.victimas)
        elif algoritmo == "IDDFS":
            resultado = busqueda_profundidad_iterativa(self.mapa, self.victimas)
        else:
            return

        self.resultado_actual = resultado
        self.lbl_stats_resumen.config(
            text=(
                f"[{resultado.algoritmo}] Rescatadas: {resultado.rescatadas}/{resultado.victimas_totales} | "
                f"Fallecidas: {resultado.fallecidas} | Ticks: {resultado.ticks_totales} | "
                f"Nodos: {resultado.nodos_expandidos} | Tiempo: {resultado.tiempo_segundos:.4f}s"
            )
        )
        messagebox.showinfo(
            "Búsqueda Completada",
            f"Algoritmo: {resultado.algoritmo}\n"
            f"Víctimas rescatadas: {resultado.rescatadas} de {resultado.victimas_totales}\n"
            f"Ticks totales: {resultado.ticks_totales}\n"
            f"Nodos expandidos: {resultado.nodos_expandidos}\n"
            f"Tiempo: {resultado.tiempo_segundos:.4f}s"
        )


def main():
    root = tk.Tk()
    app = AppRescate(root)
    root.mainloop()


if __name__ == "__main__":
    main()

