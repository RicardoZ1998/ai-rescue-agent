import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, Tuple, Set

from src.modelos_de_datos import MapaDelEntorno, VictimaEnRiesgo
from src.cargador_de_archivos import cargar_mapa_desde_archivo, cargar_victimas_desde_archivo
from src.algoritmos_de_busqueda.resultado_de_busqueda import ResultadoDeLaBusqueda
from src.algoritmos_de_busqueda.busqueda_en_amplitud import ejecutar_busqueda_en_amplitud
from src.algoritmos_de_busqueda.busqueda_de_costo_uniforme import ejecutar_busqueda_de_costo_uniforme
from src.algoritmos_de_busqueda.busqueda_en_profundidad_iterativa import ejecutar_busqueda_en_profundidad_iterativa
from src.algoritmos_de_busqueda.busqueda_a_estrella import ejecutar_busqueda_a_estrella


class AplicacionDeRescate:
    def __init__(self, ventana_raiz: tk.Tk):
        self.ventana_raiz = ventana_raiz
        self.ventana_raiz.title("Agente de Rescate con Víctimas en Riesgo - Inteligencia Artificial")
        self.ventana_raiz.geometry("1200x820")
        self.ventana_raiz.minsize(1000, 700)

        self.estilos = ttk.Style()
        self.estilos.theme_use("clam")

        self.estilos.configure("Treeview.Heading", font=("Helvetica", 9, "bold"))
        self.estilos.configure("Treeview", font=("Consolas", 9), rowheight=24)

        self.ruta_mapa: Optional[str] = None
        self.ruta_victimas: Optional[str] = None
        self.mapa_del_entorno: Optional[MapaDelEntorno] = None
        self.diccionario_de_victimas: Optional[Dict[str, VictimaEnRiesgo]] = None
        self.resultado_actual: Optional[ResultadoDeLaBusqueda] = None

        self.animacion_activa: bool = False
        self.animacion_pausada: bool = False
        self.paso_actual: int = 0
        self.identificador_del_temporizador = None
        
        self.victimas_salvadas_anim: Set[str] = set()
        self.victimas_muertas_anim: Set[str] = set()

        self._construir_interfaz_de_usuario()

    def _construir_interfaz_de_usuario(self):
        contenedor_principal_horizontal = ttk.PanedWindow(self.ventana_raiz, orient=tk.HORIZONTAL)
        contenedor_principal_horizontal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columna_de_controles = ttk.Frame(contenedor_principal_horizontal, width=350, padding=10)
        contenedor_principal_horizontal.add(columna_de_controles, weight=1)

        self._crear_panel_archivos(columna_de_controles)
        self._crear_panel_configuracion(columna_de_controles)
        self._crear_panel_resumen_mapa(columna_de_controles)

        columna_de_visualizacion = ttk.Frame(contenedor_principal_horizontal, padding=10)
        contenedor_principal_horizontal.add(columna_de_visualizacion, weight=3)

        barra_superior_del_visor = ttk.Frame(columna_de_visualizacion)
        barra_superior_del_visor.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(barra_superior_del_visor, text="Visualización del Entorno de Rescate", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        self.lbl_tick_actual = ttk.Label(barra_superior_del_visor, text="Tick: 0", font=("Consolas", 12, "bold"), foreground="#0066CC")
        self.lbl_tick_actual.pack(side=tk.RIGHT)

        self.canvas_frame = ttk.Frame(columna_de_visualizacion, borderwidth=2, relief=tk.GROOVE)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.canvas = tk.Canvas(self.canvas_frame, bg="#2C3437")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._mostrar_placeholder_canvas()
        self._crear_leyenda_colores(columna_de_visualizacion)
        self._crear_panel_estadisticas_y_tabla(columna_de_visualizacion)

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
        contenedor_de_leyenda_de_colores = ttk.Frame(parent)
        contenedor_de_leyenda_de_colores.pack(fill=tk.X, pady=(0, 8))

        elementos_de_la_leyenda = [
            ("Muro (#)", "#1F2421", "white"),
            ("Agente (A)", "#3498DB", "white"),
            ("Víctima Viva", "#F39C12", "white"),
            ("Rescatada (Verde)", "#27AE60", "white"),
            ("Fallecida (Rojo)", "#E74C3C", "white")
        ]

        for nombre_del_elemento, color_de_fondo, color_del_texto in elementos_de_la_leyenda:
            etiqueta_leyenda = tk.Label(contenedor_de_leyenda_de_colores, text=f" {nombre_del_elemento} ", bg=color_de_fondo, fg=color_del_texto, font=("Helvetica", 8, "bold"), relief=tk.RIDGE)
            etiqueta_leyenda.pack(side=tk.LEFT, padx=3)

    def _crear_panel_archivos(self, parent: ttk.Frame):
        contenedor_de_carga_de_archivos = ttk.LabelFrame(parent, text="1. Carga de Archivos", padding=10)
        contenedor_de_carga_de_archivos.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(contenedor_de_carga_de_archivos, text="Archivo de Mapa:", font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
        fila_del_boton_mapa = ttk.Frame(contenedor_de_carga_de_archivos)
        fila_del_boton_mapa.pack(fill=tk.X, pady=(2, 6))

        self.btn_mapa = ttk.Button(fila_del_boton_mapa, text="Examinar...", command=self._examinar_mapa)
        self.btn_mapa.pack(side=tk.LEFT)

        self.lbl_estado_mapa = ttk.Label(fila_del_boton_mapa, text="  [No cargado]", foreground="red")
        self.lbl_estado_mapa.pack(side=tk.LEFT, padx=5)

        self.lbl_ruta_mapa = ttk.Label(contenedor_de_carga_de_archivos, text="Ningún archivo seleccionado", font=("Helvetica", 8), foreground="#666666")
        self.lbl_ruta_mapa.pack(anchor=tk.W, pady=(0, 8))

        ttk.Label(contenedor_de_carga_de_archivos, text="Archivo de Víctimas:", font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
        fila_del_boton_victimas = ttk.Frame(contenedor_de_carga_de_archivos)
        fila_del_boton_victimas.pack(fill=tk.X, pady=(2, 6))

        self.btn_victimas = ttk.Button(fila_del_boton_victimas, text="Examinar...", command=self._examinar_victimas)
        self.btn_victimas.pack(side=tk.LEFT)

        self.lbl_estado_vic = ttk.Label(fila_del_boton_victimas, text="  [No cargado]", foreground="red")
        self.lbl_estado_vic.pack(side=tk.LEFT, padx=5)

        self.lbl_ruta_vic = ttk.Label(contenedor_de_carga_de_archivos, text="Ningún archivo seleccionado", font=("Helvetica", 8), foreground="#666666")
        self.lbl_ruta_vic.pack(anchor=tk.W)

    def _crear_panel_configuracion(self, parent: ttk.Frame):
        contenedor_de_configuracion = ttk.LabelFrame(parent, text="2. Configuración de Simulación", padding=10)
        contenedor_de_configuracion.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(contenedor_de_configuracion, text="Seleccionar Algoritmo:", font=("Helvetica", 9, "bold")).pack(anchor=tk.W, pady=(0, 4))
        self.combo_algoritmo = ttk.Combobox(
            contenedor_de_configuracion,
            values=["A*", "BFS", "UCS", "IDDFS"],
            state="readonly"
        )
        self.combo_algoritmo.current(0)
        self.combo_algoritmo.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(contenedor_de_configuracion, text="Velocidad (ms por tick):", font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
        fila_del_control_de_velocidad = ttk.Frame(contenedor_de_configuracion)
        fila_del_control_de_velocidad.pack(fill=tk.X, pady=(2, 10))

        self.scale_velocidad = ttk.Scale(fila_del_control_de_velocidad, from_=50, to=1000, value=300, orient=tk.HORIZONTAL)
        self.scale_velocidad.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.lbl_vel_val = ttk.Label(fila_del_control_de_velocidad, text="300 ms", width=8, font=("Consolas", 9))
        self.lbl_vel_val.pack(side=tk.RIGHT, padx=5)
        self.scale_velocidad.configure(command=self._actualizar_etiqueta_velocidad)

        self.btn_iniciar = ttk.Button(contenedor_de_configuracion, text="🚀 Iniciar Rescate", command=self._iniciar_rescate)
        self.btn_iniciar.pack(fill=tk.X, ipady=4, pady=(2, 4))

        fila_de_botones_de_animacion = ttk.Frame(contenedor_de_configuracion)
        fila_de_botones_de_animacion.pack(fill=tk.X, pady=(2, 6))

        self.btn_pausa = ttk.Button(fila_de_botones_de_animacion, text="⏸ Pausar", command=self._pausar_animacion, state=tk.DISABLED)
        self.btn_pausa.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        self.btn_reiniciar = ttk.Button(fila_de_botones_de_animacion, text="🔄 Reiniciar", command=self._reiniciar_animacion, state=tk.DISABLED)
        self.btn_reiniciar.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))

        self.btn_comparar_todos = ttk.Button(
            contenedor_de_configuracion,
            text="📊 Comparar los 4 Algoritmos",
            command=self._comparar_todos_los_algoritmos
        )
        self.btn_comparar_todos.pack(fill=tk.X, ipady=3, pady=(4, 0))

    def _crear_panel_resumen_mapa(self, parent: ttk.Frame):
        contenedor_de_informacion_del_mapa = ttk.LabelFrame(parent, text="Información del Mapa", padding=10)
        contenedor_de_informacion_del_mapa.pack(fill=tk.BOTH, expand=True)

        self.lbl_info_mapa = ttk.Label(
            contenedor_de_informacion_del_mapa,
            text="Dimensiones: ---\nPosición Inicio: ---\nTotal Víctimas: ---",
            font=("Consolas", 9)
        )
        self.lbl_info_mapa.pack(anchor=tk.W)

    def _crear_panel_estadisticas_y_tabla(self, parent: ttk.Frame):
        contenedor_de_estadisticas = ttk.LabelFrame(parent, text="5. Estadísticas de Ejecución y Comparación", padding=10)
        contenedor_de_estadisticas.pack(fill=tk.BOTH, expand=False)

        fila_de_estadisticas_y_tabla = ttk.Frame(contenedor_de_estadisticas)
        fila_de_estadisticas_y_tabla.pack(fill=tk.BOTH, expand=True)

        contenedor_de_resumen_individual = ttk.LabelFrame(fila_de_estadisticas_y_tabla, text="RESULTADO DE LA SIMULACIÓN", padding=8)
        contenedor_de_resumen_individual.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.lbl_resumen_detallado = ttk.Label(
            contenedor_de_resumen_individual,
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

        contenedor_de_tabla_comparativa = ttk.LabelFrame(fila_de_estadisticas_y_tabla, text="COMPARACIÓN DE ALGORITMOS", padding=8)
        contenedor_de_tabla_comparativa.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        nombres_de_columnas_de_la_tabla = ("algoritmo", "nodos", "tiempo", "rescatadas", "fallecidas", "ticks")
        self.tree_comparacion = ttk.Treeview(contenedor_de_tabla_comparativa, columns=nombres_de_columnas_de_la_tabla, show="headings", height=5)

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
        milisegundos_de_velocidad = int(float(val))
        self.lbl_vel_val.config(text=f"{milisegundos_de_velocidad} ms")

    def _examinar_mapa(self):
        ruta_del_archivo_seleccionado = filedialog.askopenfilename(
            title="Seleccionar mapa.txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialdir=os.path.abspath("data")
        )
        if not ruta_del_archivo_seleccionado:
            return

        try:
            mapa = cargar_mapa_desde_archivo(ruta_del_archivo_seleccionado)
            self.mapa_del_entorno = mapa
            self.ruta_mapa = ruta_del_archivo_seleccionado
            self.lbl_ruta_mapa.config(text=os.path.basename(ruta_del_archivo_seleccionado))
            self.lbl_estado_mapa.config(text="  [✓ Correcto]", foreground="#00AA00")
            self._actualizar_info()
            self._dibujar_mapa_estatico()
        except Exception as e:
            self.mapa_del_entorno = None
            self.lbl_estado_mapa.config(text="  [✗ Error]", foreground="red")
            messagebox.showerror("Error en Mapa", str(e))

    def _examinar_victimas(self):
        ruta_del_archivo_seleccionado = filedialog.askopenfilename(
            title="Seleccionar victimas.txt",
            filetypes=[("Archivos de texto o CSV", "*.txt *.csv"), ("Todos los archivos", "*.*")],
            initialdir=os.path.abspath("data")
        )
        if not ruta_del_archivo_seleccionado:
            return

        try:
            victimas = cargar_victimas_desde_archivo(ruta_del_archivo_seleccionado, mapa_del_entorno=self.mapa_del_entorno)
            self.diccionario_de_victimas = victimas
            self.ruta_victimas = ruta_del_archivo_seleccionado
            self.lbl_ruta_vic.config(text=os.path.basename(ruta_del_archivo_seleccionado))
            self.lbl_estado_vic.config(text="  [✓ Correcto]", foreground="#00AA00")
            self._actualizar_info()
            self._dibujar_mapa_estatico()
        except Exception as e:
            self.diccionario_de_victimas = None
            self.lbl_estado_vic.config(text="  [✗ Error]", foreground="red")
            messagebox.showerror("Error en Víctimas", str(e))

    def _actualizar_info(self):
        texto_informacion_del_mapa = f"Dimensiones: {self.mapa_del_entorno.filas}x{self.mapa_del_entorno.columnas}\nInicio 'S': {self.mapa_del_entorno.posicion_de_inicio}" if self.mapa_del_entorno else "Dimensiones: ---\nInicio 'S': ---"
        texto_informacion_de_victimas = f"\nTotal Víctimas: {len(self.diccionario_de_victimas)}" if self.diccionario_de_victimas else "\nTotal Víctimas: ---"
        self.lbl_info_mapa.config(text=texto_informacion_del_mapa + texto_informacion_de_victimas)

    def _dibujar_mapa_estatico(self, posicion_del_agente: Optional[Tuple[int, int]] = None, tick_actual: int = 0):
        if not self.mapa_del_entorno:
            return

        self.canvas.delete("all")
        ancho_del_lienzo = self.canvas.winfo_width()
        alto_del_lienzo = self.canvas.winfo_height()

        if ancho_del_lienzo < 50 or alto_del_lienzo < 50:
            ancho_del_lienzo = 650
            alto_del_lienzo = 380

        margen_exterior_del_lienzo = 20
        ancho_calculado_de_celda = (ancho_del_lienzo - 2 * margen_exterior_del_lienzo) / self.mapa_del_entorno.columnas
        alto_calculado_de_celda = (alto_del_lienzo - 2 * margen_exterior_del_lienzo) / self.mapa_del_entorno.filas
        tamano_final_de_celda = max(18, min(ancho_calculado_de_celda, alto_calculado_de_celda, 60))

        desplazamiento_horizontal_para_centrar = (ancho_del_lienzo - (tamano_final_de_celda * self.mapa_del_entorno.columnas)) / 2
        desplazamiento_vertical_para_centrar = (alto_del_lienzo - (tamano_final_de_celda * self.mapa_del_entorno.filas)) / 2

        if posicion_del_agente is None:
            posicion_del_agente = self.mapa_del_entorno.posicion_de_inicio

        for indice_fila in range(self.mapa_del_entorno.filas):
            for indice_columna in range(self.mapa_del_entorno.columnas):
                esquina_izquierda = desplazamiento_horizontal_para_centrar + indice_columna * tamano_final_de_celda
                esquina_superior = desplazamiento_vertical_para_centrar + indice_fila * tamano_final_de_celda
                esquina_derecha = esquina_izquierda + tamano_final_de_celda
                esquina_inferior = esquina_superior + tamano_final_de_celda

                caracter_de_la_celda = self.mapa_del_entorno.celdas[indice_fila][indice_columna]
                if caracter_de_la_celda == '#':
                    self.canvas.create_rectangle(esquina_izquierda, esquina_superior, esquina_derecha, esquina_inferior, fill="#1F2421", outline="#34495E")
                else:
                    self.canvas.create_rectangle(esquina_izquierda, esquina_superior, esquina_derecha, esquina_inferior, fill="#ECEFF1", outline="#BDC3C7")

        fila_inicio, columna_inicio = self.mapa_del_entorno.posicion_de_inicio
        inicio_x = desplazamiento_horizontal_para_centrar + columna_inicio * tamano_final_de_celda
        inicio_y = desplazamiento_vertical_para_centrar + fila_inicio * tamano_final_de_celda
        self.canvas.create_text(
            inicio_x + tamano_final_de_celda / 2, inicio_y + tamano_final_de_celda / 2,
            text="S", fill="#7F8C8D", font=("Helvetica", int(tamano_final_de_celda * 0.4), "bold")
        )

        if self.diccionario_de_victimas:
            for victima_actual in self.diccionario_de_victimas.values():
                victima_x1 = desplazamiento_horizontal_para_centrar + victima_actual.columna * tamano_final_de_celda
                victima_y1 = desplazamiento_vertical_para_centrar + victima_actual.fila * tamano_final_de_celda
                victima_x2 = victima_x1 + tamano_final_de_celda
                victima_y2 = victima_y1 + tamano_final_de_celda

                ticks_de_vida_restantes = victima_actual.ticks_supervivencia - tick_actual

                if victima_actual.identificador in self.victimas_salvadas_anim:
                    color_de_fondo_de_la_victima = "#27AE60"
                    texto_del_estado_de_la_victima = f"{victima_actual.identificador}\n✓ SALVADA"
                elif victima_actual.identificador in self.victimas_muertas_anim or ticks_de_vida_restantes < 0:
                    color_de_fondo_de_la_victima = "#E74C3C"
                    texto_del_estado_de_la_victima = f"{victima_actual.identificador}\n✗ MUERTA"
                else:
                    color_de_fondo_de_la_victima = "#F39C12"
                    texto_del_estado_de_la_victima = f"{victima_actual.identificador}\n⏱ {ticks_de_vida_restantes}"

                margen_interior_de_la_celda = tamano_final_de_celda * 0.08
                self.canvas.create_oval(victima_x1 + margen_interior_de_la_celda, victima_y1 + margen_interior_de_la_celda, victima_x2 - margen_interior_de_la_celda, victima_y2 - margen_interior_de_la_celda, fill=color_de_fondo_de_la_victima, outline="#FFFFFF", width=2)
                self.canvas.create_text(
                    victima_x1 + tamano_final_de_celda / 2, victima_y1 + tamano_final_de_celda / 2,
                    text=texto_del_estado_de_la_victima, fill="#FFFFFF",
                    font=("Helvetica", max(7, int(tamano_final_de_celda * 0.22)), "bold"),
                    justify=tk.CENTER
                )

        fila_del_agente, columna_del_agente = posicion_del_agente
        agente_x1 = desplazamiento_horizontal_para_centrar + columna_del_agente * tamano_final_de_celda
        agente_y1 = desplazamiento_vertical_para_centrar + fila_del_agente * tamano_final_de_celda
        agente_x2 = agente_x1 + tamano_final_de_celda
        agente_y2 = agente_y1 + tamano_final_de_celda

        margen_interior_del_agente = tamano_final_de_celda * 0.15
        self.canvas.create_rectangle(
            agente_x1 + margen_interior_del_agente, agente_y1 + margen_interior_del_agente, agente_x2 - margen_interior_del_agente, agente_y2 - margen_interior_del_agente,
            fill="#2980B9", outline="#F1C40F", width=3
        )
        self.canvas.create_text(
            agente_x1 + tamano_final_de_celda / 2, agente_y1 + tamano_final_de_celda / 2,
            text="AGENTE", fill="#FFFFFF",
            font=("Helvetica", max(7, int(tamano_final_de_celda * 0.2)), "bold")
        )

    def _iniciar_rescate(self):
        if not self.mapa_del_entorno:
            messagebox.showwarning("Falta Mapa", "Por favor cargue un archivo de mapa válido primero.")
            return
        if not self.diccionario_de_victimas:
            messagebox.showwarning("Faltan Víctimas", "Por favor cargue un archivo de víctimas válido primero.")
            return

        if self.identificador_del_temporizador:
            self.ventana_raiz.after_cancel(self.identificador_del_temporizador)
            self.identificador_del_temporizador = None

        nombre_del_algoritmo_seleccionado = self.combo_algoritmo.get()

        if nombre_del_algoritmo_seleccionado == "A*":
            resultado_de_la_busqueda = ejecutar_busqueda_a_estrella(self.mapa_del_entorno, self.diccionario_de_victimas)
        elif nombre_del_algoritmo_seleccionado == "BFS":
            resultado_de_la_busqueda = ejecutar_busqueda_en_amplitud(self.mapa_del_entorno, self.diccionario_de_victimas)
        elif nombre_del_algoritmo_seleccionado == "UCS":
            resultado_de_la_busqueda = ejecutar_busqueda_de_costo_uniforme(self.mapa_del_entorno, self.diccionario_de_victimas)
        elif nombre_del_algoritmo_seleccionado == "IDDFS":
            resultado_de_la_busqueda = ejecutar_busqueda_en_profundidad_iterativa(self.mapa_del_entorno, self.diccionario_de_victimas, limite_maximo_cota=16)
        else:
            return

        self.resultado_actual = resultado_de_la_busqueda
        self._actualizar_panel_resumen_individual(resultado_de_la_busqueda)
        self._actualizar_fila_tabla(resultado_de_la_busqueda)

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

        secuencia_de_pasos_del_camino = self.resultado_actual.camino
        if self.paso_actual < len(secuencia_de_pasos_del_camino):
            accion_realizada, fila_del_agente, columna_del_agente = secuencia_de_pasos_del_camino[self.paso_actual]
            tick_del_paso_actual = self.paso_actual
            self.lbl_tick_actual.config(text=f"Tick: {tick_del_paso_actual} ({accion_realizada if accion_realizada else 'Inicio'})")

            for victima_actual in self.diccionario_de_victimas.values():
                if victima_actual.identificador in self.victimas_salvadas_anim:
                    continue
                if victima_actual.fila == fila_del_agente and victima_actual.columna == columna_del_agente:
                    if tick_del_paso_actual <= victima_actual.ticks_supervivencia:
                        self.victimas_salvadas_anim.add(victima_actual.identificador)
                else:
                    if tick_del_paso_actual > victima_actual.ticks_supervivencia:
                        self.victimas_muertas_anim.add(victima_actual.identificador)

            self._dibujar_mapa_estatico(posicion_del_agente=(fila_del_agente, columna_del_agente), tick_actual=tick_del_paso_actual)

            self.paso_actual += 1
            retardo_en_milisegundos = int(self.scale_velocidad.get())
            self.identificador_del_temporizador = self.ventana_raiz.after(retardo_en_milisegundos, self._siguiente_paso_animacion)
        else:
            self.animacion_activa = False
            self.btn_iniciar.config(state=tk.NORMAL)
            self.btn_pausa.config(state=tk.DISABLED)

    def _actualizar_panel_resumen_individual(self, resultado_de_busqueda: ResultadoDeLaBusqueda):
        texto_del_resumen = (
            f"Víctimas totales    : {resultado_de_busqueda.victimas_totales}\n"
            f"Víctimas rescatadas : {resultado_de_busqueda.rescatadas}  (✓)\n"
            f"Víctimas fallecidas : {resultado_de_busqueda.fallecidas}  (✗)\n"
            f"Ticks totales       : {resultado_de_busqueda.ticks_totales}\n"
            f"Nodos expandidos    : {resultado_de_busqueda.nodos_expandidos}\n"
            f"Tiempo de cómputo   : {resultado_de_busqueda.tiempo_segundos:.4f}s"
        )
        self.lbl_resumen_detallado.config(text=texto_del_resumen)

    def _actualizar_fila_tabla(self, resultado_de_busqueda: ResultadoDeLaBusqueda):
        for identificador_de_fila in self.tree_comparacion.get_children():
            if self.tree_comparacion.item(identificador_de_fila, "values")[0] == resultado_de_busqueda.algoritmo:
                self.tree_comparacion.delete(identificador_de_fila)

        valores_de_la_fila = (
            resultado_de_busqueda.algoritmo,
            str(resultado_de_busqueda.nodos_expandidos),
            f"{resultado_de_busqueda.tiempo_segundos:.4f}s",
            str(resultado_de_busqueda.rescatadas),
            str(resultado_de_busqueda.fallecidas),
            str(resultado_de_busqueda.ticks_totales)
        )
        self.tree_comparacion.insert("", tk.END, values=valores_de_la_fila)

    def _comparar_todos_los_algoritmos(self):
        if not self.mapa_del_entorno or not self.diccionario_de_victimas:
            messagebox.showwarning("Datos Requeridos", "Debe cargar el mapa y las víctimas antes de comparar.")
            return

        for identificador_de_fila in self.tree_comparacion.get_children():
            self.tree_comparacion.delete(identificador_de_fila)

        lista_de_funciones_de_busqueda = [
            ejecutar_busqueda_en_amplitud,
            ejecutar_busqueda_de_costo_uniforme,
            lambda mapa_param, victimas_param: ejecutar_busqueda_en_profundidad_iterativa(mapa_param, victimas_param, limite_maximo_cota=16),
            ejecutar_busqueda_a_estrella
        ]

        for funcion_de_busqueda in lista_de_funciones_de_busqueda:
            resultado_de_la_busqueda = funcion_de_busqueda(self.mapa_del_entorno, self.diccionario_de_victimas)
            self._actualizar_fila_tabla(resultado_de_la_busqueda)

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
            if self.identificador_del_temporizador:
                self.ventana_raiz.after_cancel(self.identificador_del_temporizador)
                self.identificador_del_temporizador = None

    def _reiniciar_animacion(self):
        if self.identificador_del_temporizador:
            self.ventana_raiz.after_cancel(self.identificador_del_temporizador)
            self.identificador_del_temporizador = None

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
    ventana_principal = tk.Tk()
    aplicacion = AplicacionDeRescate(ventana_principal)
    ventana_principal.mainloop()


if __name__ == "__main__":
    main()

