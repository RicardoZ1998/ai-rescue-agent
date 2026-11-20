"""
Interfaz Gráfica de Usuario (GUI) construida exclusivamente con Tkinter nativo.
Incluye Lienzo Canvas animado y Panel de Estadísticas con Tabla Comparativa (Tarjeta 4.3).
"""

# Módulo "os": se usa para manejar rutas de archivos (abspath, basename).
import os
# Tkinter (GUI estándar de Python) con el alias "tk".
import tkinter as tk
# ttk = widgets con apariencia moderna; filedialog = ventana "Examinar"; messagebox = cuadros de aviso/error.
from tkinter import ttk, filedialog, messagebox
# Tipos para anotaciones.
from typing import Optional, Dict, List, Tuple, Set

# Clases del modelo: el mapa y las víctimas.
from src.models import Mapa, Victima
# Funciones que leen y validan los archivos de entrada.
from src.loader import cargar_mapa, cargar_victimas
# Algoritmo BFS y la clase de resultado.
from src.algorithms.bfs import busqueda_amplitud, ResultadoBusqueda
# Algoritmo UCS.
from src.algorithms.ucs import busqueda_costo_uniforme
# Algoritmo IDDFS.
from src.algorithms.iddfs import busqueda_profundidad_iterativa
# Algoritmo A*.
from src.algorithms.astar import busqueda_a_estrella


# Clase que representa toda la aplicación (ventana + lógica).
class AppRescate:
    """
    Ventana principal de escritorio para el Agente de Rescate con simulación animada,
    panel de estadísticas individuales y tabla comparativa de los 4 algoritmos.
    """
    # Constructor: recibe la ventana raíz creada en main.py.
    def __init__(self, root: tk.Tk):
        # Guarda la ventana raíz para usarla en otros métodos.
        self.root = root
        # Pone el título que aparece en la barra de la ventana.
        self.root.title("Agente de Rescate con Víctimas en Riesgo - Inteligencia Artificial")
        # Tamaño inicial de la ventana: 1200 de ancho por 820 de alto.
        self.root.geometry("1200x820")
        # Tamaño mínimo permitido al redimensionar.
        self.root.minsize(1000, 700)

        # Objeto de estilos de ttk (para cambiar la apariencia de los widgets).
        self.style = ttk.Style()
        # Usa el tema "clam", que se ve parecido en todos los sistemas operativos.
        self.style.theme_use("clam")

        # Configurar estilos de tablas y botones
        # Fuente en negrita para los encabezados de la tabla (Treeview).
        self.style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"))
        # Fuente monoespaciada y alto de fila de 24 px para el cuerpo de la tabla.
        self.style.configure("Treeview", font=("Consolas", 9), rowheight=24)

        # Estado de datos
        # Ruta del archivo de mapa elegido (None = todavía no se ha cargado).
        self.ruta_mapa: Optional[str] = None
        # Ruta del archivo de víctimas elegido.
        self.ruta_victimas: Optional[str] = None
        # Objeto Mapa ya cargado y validado.
        self.mapa: Optional[Mapa] = None
        # Diccionario {id: Victima} ya cargado.
        self.victimas: Optional[Dict[str, Victima]] = None
        # Último resultado de búsqueda (el que se está animando).
        self.resultado_actual: Optional[ResultadoBusqueda] = None

        # Variables de control de la animación
        # ¿La animación está corriendo?
        self.animacion_activa: bool = False
        # ¿La animación está en pausa?
        self.animacion_pausada: bool = False
        # Índice del paso del camino que toca dibujar (0 = estado inicial).
        self.paso_actual: int = 0
        # Identificador del temporizador de Tkinter (after) para poder cancelarlo.
        self.after_id = None
        
        # IDs de víctimas que la animación ya marcó como salvadas.
        self.victimas_salvadas_anim: Set[str] = set()
        # IDs de víctimas que la animación ya marcó como muertas.
        self.victimas_muertas_anim: Set[str] = set()

        # Construye todos los widgets de la ventana.
        self._construir_interfaz()

    # Arma la estructura general: columna izquierda (controles) y derecha (mapa y resultados).
    def _construir_interfaz(self):
        # Panel dividido horizontalmente en dos zonas (izquierda y derecha).
        panel_principal = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        # Lo coloca ocupando toda la ventana, con 10 px de margen.
        panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ==========================================
        # COLUMNA IZQUIERDA: CONTROLES
        # ==========================================
        # Contenedor de la columna izquierda (ancho inicial 350).
        col_izquierda = ttk.Frame(panel_principal, width=350, padding=10)
        # Lo agrega al panel dividido con peso 1 (ocupa menos espacio que la derecha).
        panel_principal.add(col_izquierda, weight=1)

        # Crea el bloque "1. Carga de Archivos".
        self._crear_panel_archivos(col_izquierda)
        # Crea el bloque "2. Configuración de Simulación".
        self._crear_panel_configuracion(col_izquierda)
        # Crea el bloque "Información del Mapa".
        self._crear_panel_resumen_mapa(col_izquierda)

        # ==========================================
        # COLUMNA DERECHA: VISUALIZACIÓN Y RESULTADOS
        # ==========================================
        # Contenedor de la columna derecha.
        col_derecha = ttk.Frame(panel_principal, padding=10)
        # Lo agrega con peso 3 (ocupa el triple de espacio que la izquierda).
        panel_principal.add(col_derecha, weight=3)

        # Barra de estado superior
        # Contenedor de la barra superior (título + contador de ticks).
        header_visor = ttk.Frame(col_derecha)
        # Se estira en horizontal; deja 5 px de espacio debajo.
        header_visor.pack(fill=tk.X, pady=(0, 5))

        # Título de la zona de visualización, a la izquierda.
        ttk.Label(header_visor, text="Visualización del Entorno de Rescate", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        # Etiqueta del tick actual (azul, monoespaciada); la animación la va actualizando.
        self.lbl_tick_actual = ttk.Label(header_visor, text="Tick: 0", font=("Consolas", 12, "bold"), foreground="#0066CC")
        # La coloca a la derecha de la barra.
        self.lbl_tick_actual.pack(side=tk.RIGHT)

        # Canvas con bordes
        # Marco con borde (relieve "groove") que rodea al canvas.
        self.canvas_frame = ttk.Frame(col_derecha, borderwidth=2, relief=tk.GROOVE)
        # Ocupa todo el espacio disponible.
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Canvas: el lienzo donde se dibuja la cuadrícula; fondo gris oscuro.
        self.canvas = tk.Canvas(self.canvas_frame, bg="#2C3437")
        # Se expande para llenar su marco.
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Dibuja el texto inicial "Cargue el mapa...".
        self._mostrar_placeholder_canvas()
        # Crea la leyenda de colores debajo del canvas.
        self._crear_leyenda_colores(col_derecha)

        # Panel de Estadísticas y Tabla Comparativa
        # Crea el panel inferior con resumen individual y tabla de comparación.
        self._crear_panel_estadisticas_y_tabla(col_derecha)

    # Muestra un mensaje de ayuda en el canvas cuando aún no hay datos cargados.
    def _mostrar_placeholder_canvas(self):
        # Borra todo lo que hubiera dibujado en el canvas.
        self.canvas.delete("all")
        # Escribe el mensaje en la posición (380, 180).
        self.canvas.create_text(
            # Coordenadas x, y del texto.
            380, 180,
            # Texto a mostrar.
            text="Cargue el mapa y las víctimas para comenzar la simulación",
            # Color gris claro.
            fill="#AAAAAA",
            # Fuente en cursiva.
            font=("Helvetica", 13, "italic"),
            # Etiqueta del objeto en el canvas.
            tags="placeholder"
        )

    # Crea la fila de etiquetas de colores que explican qué significa cada color del mapa.
    def _crear_leyenda_colores(self, parent: ttk.Frame):
        # Contenedor de la leyenda dentro del padre.
        frame_leyenda = ttk.Frame(parent)
        # Se estira en horizontal, con 8 px de espacio debajo.
        frame_leyenda.pack(fill=tk.X, pady=(0, 8))

        # Lista de (texto, color de fondo, color de letra) para cada elemento de la leyenda.
        elementos = [
            # Paredes.
            ("Muro (#)", "#1F2421", "white"),
            # Agente.
            ("Agente (A)", "#3498DB", "white"),
            # Víctima viva.
            ("Víctima Viva", "#F39C12", "white"),
            # Víctima rescatada.
            ("Rescatada (Verde)", "#27AE60", "white"),
            # Víctima fallecida.
            ("Fallecida (Rojo)", "#E74C3C", "white")
        ]

        # Recorre cada elemento de la leyenda.
        for nombre, color_bg, color_fg in elementos:
            # Crea una etiqueta coloreada (se usa tk.Label porque admite bg/fg directamente).
            lbl = tk.Label(frame_leyenda, text=f" {nombre} ", bg=color_bg, fg=color_fg, font=("Helvetica", 8, "bold"), relief=tk.RIDGE)
            # La coloca a la izquierda, con 3 px de separación horizontal.
            lbl.pack(side=tk.LEFT, padx=3)

    # Panel "1. Carga de Archivos": botones Examinar + indicadores de estado y ruta.
    def _crear_panel_archivos(self, parent: ttk.Frame):
        # Marco con título para agrupar el bloque.
        frame_archivos = ttk.LabelFrame(parent, text="1. Carga de Archivos", padding=10)
        # Se estira en horizontal, con 10 px de espacio debajo.
        frame_archivos.pack(fill=tk.X, pady=(0, 10))

        # Etiqueta "Archivo de Mapa:", alineada a la izquierda (anchor=W).
        ttk.Label(frame_archivos, text="Archivo de Mapa:", font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
        # Fila que contendrá el botón y el indicador del mapa.
        fila_mapa = ttk.Frame(frame_archivos)
        # Se estira en horizontal, con pequeños espacios arriba y abajo.
        fila_mapa.pack(fill=tk.X, pady=(2, 6))

        # Botón "Examinar..." para el mapa: al pulsarlo llama a _examinar_mapa.
        self.btn_mapa = ttk.Button(fila_mapa, text="Examinar...", command=self._examinar_mapa)
        # Lo coloca a la izquierda de la fila.
        self.btn_mapa.pack(side=tk.LEFT)

        # Indicador de lectura del mapa: empieza en rojo "[No cargado]".
        self.lbl_estado_mapa = ttk.Label(fila_mapa, text="  [No cargado]", foreground="red")
        # Lo coloca junto al botón, con 5 px de separación.
        self.lbl_estado_mapa.pack(side=tk.LEFT, padx=5)

        # Etiqueta que mostrará el nombre del archivo de mapa elegido (gris, letra pequeña).
        self.lbl_ruta_mapa = ttk.Label(frame_archivos, text="Ningún archivo seleccionado", font=("Helvetica", 8), foreground="#666666")
        # La coloca alineada a la izquierda.
        self.lbl_ruta_mapa.pack(anchor=tk.W, pady=(0, 8))

        # Etiqueta "Archivo de Víctimas:".
        ttk.Label(frame_archivos, text="Archivo de Víctimas:", font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
        # Fila para el botón e indicador de víctimas.
        fila_vic = ttk.Frame(frame_archivos)
        # Se estira en horizontal.
        fila_vic.pack(fill=tk.X, pady=(2, 6))

        # Botón "Examinar..." para víctimas: llama a _examinar_victimas.
        self.btn_victimas = ttk.Button(fila_vic, text="Examinar...", command=self._examinar_victimas)
        # Lo coloca a la izquierda.
        self.btn_victimas.pack(side=tk.LEFT)

        # Indicador de lectura del archivo de víctimas (inicia en rojo).
        self.lbl_estado_vic = ttk.Label(fila_vic, text="  [No cargado]", foreground="red")
        # Lo coloca junto al botón.
        self.lbl_estado_vic.pack(side=tk.LEFT, padx=5)

        # Etiqueta con el nombre del archivo de víctimas elegido.
        self.lbl_ruta_vic = ttk.Label(frame_archivos, text="Ningún archivo seleccionado", font=("Helvetica", 8), foreground="#666666")
        # La coloca alineada a la izquierda.
        self.lbl_ruta_vic.pack(anchor=tk.W)

    # Panel "2. Configuración de Simulación": algoritmo, velocidad y botones de control.
    def _crear_panel_configuracion(self, parent: ttk.Frame):
        # Marco con título para este bloque.
        frame_config = ttk.LabelFrame(parent, text="2. Configuración de Simulación", padding=10)
        # Se estira en horizontal.
        frame_config.pack(fill=tk.X, pady=(0, 10))

        # Etiqueta "Seleccionar Algoritmo:".
        ttk.Label(frame_config, text="Seleccionar Algoritmo:", font=("Helvetica", 9, "bold")).pack(anchor=tk.W, pady=(0, 4))
        # Menú desplegable (Combobox) con los 4 algoritmos.
        self.combo_algoritmo = ttk.Combobox(
            # Su contenedor.
            frame_config,
            # Opciones disponibles (la primera, "A*", es la predeterminada).
            values=["A*", "BFS", "UCS", "IDDFS"],
            # "readonly": solo se puede elegir de la lista, no escribir texto libre.
            state="readonly"
        )
        # Selecciona la primera opción (índice 0 = "A*") por defecto.
        self.combo_algoritmo.current(0)
        # Lo coloca ocupando todo el ancho del bloque.
        self.combo_algoritmo.pack(fill=tk.X, pady=(0, 10))

        # Etiqueta "Velocidad (ms por tick):".
        ttk.Label(frame_config, text="Velocidad (ms por tick):", font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
        # Fila que contiene el deslizador y su valor numérico.
        fila_vel = ttk.Frame(frame_config)
        # Se estira en horizontal.
        fila_vel.pack(fill=tk.X, pady=(2, 10))

        # Deslizador de 50 a 1000 ms con valor inicial 300, horizontal.
        self.scale_velocidad = ttk.Scale(fila_vel, from_=50, to=1000, value=300, orient=tk.HORIZONTAL)
        # Lo coloca a la izquierda y lo deja crecer para llenar el espacio.
        self.scale_velocidad.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Etiqueta que muestra el valor actual del deslizador ("300 ms").
        self.lbl_vel_val = ttk.Label(fila_vel, text="300 ms", width=8, font=("Consolas", 9))
        # La coloca a la derecha del deslizador.
        self.lbl_vel_val.pack(side=tk.RIGHT, padx=5)
        # Cada vez que se mueva el deslizador, se llama a _actualizar_etiqueta_velocidad.
        self.scale_velocidad.configure(command=self._actualizar_etiqueta_velocidad)

        # Botones de control
        # Botón principal: ejecuta el algoritmo y lanza la animación.
        self.btn_iniciar = ttk.Button(frame_config, text="🚀 Iniciar Rescate", command=self._iniciar_rescate)
        # Lo coloca a todo el ancho, un poco más alto (ipady=4).
        self.btn_iniciar.pack(fill=tk.X, ipady=4, pady=(2, 4))

        # Fila para los botones Pausar y Reiniciar.
        fila_botones_anim = ttk.Frame(frame_config)
        # Se estira en horizontal.
        fila_botones_anim.pack(fill=tk.X, pady=(2, 6))

        # Botón Pausar: empieza deshabilitado (no hay animación aún).
        self.btn_pausa = ttk.Button(fila_botones_anim, text="⏸ Pausar", command=self._pausar_animacion, state=tk.DISABLED)
        # Lo coloca a la izquierda y lo estira para repartir el espacio.
        self.btn_pausa.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        # Botón Reiniciar: también empieza deshabilitado.
        self.btn_reiniciar = ttk.Button(fila_botones_anim, text="🔄 Reiniciar", command=self._reiniciar_animacion, state=tk.DISABLED)
        # Lo coloca a la derecha y lo estira.
        self.btn_reiniciar.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))

        # Botón para ejecutar la comparación de los 4 algoritmos de una vez
        # Crea el botón de comparar todos.
        self.btn_comparar_todos = ttk.Button(
            # Su contenedor.
            frame_config,
            # Texto del botón.
            text="📊 Comparar los 4 Algoritmos",
            # Método que se ejecuta al pulsarlo.
            command=self._comparar_todos_los_algoritmos
        )
        # Lo coloca a todo el ancho.
        self.btn_comparar_todos.pack(fill=tk.X, ipady=3, pady=(4, 0))

    # Panel "Información del Mapa": muestra dimensiones, posición de inicio y total de víctimas.
    def _crear_panel_resumen_mapa(self, parent: ttk.Frame):
        # Marco con título.
        frame_info = ttk.LabelFrame(parent, text="Información del Mapa", padding=10)
        # Ocupa el espacio restante de la columna izquierda.
        frame_info.pack(fill=tk.BOTH, expand=True)

        # Etiqueta multilínea con valores "---" hasta que se carguen los archivos.
        self.lbl_info_mapa = ttk.Label(
            # Su contenedor.
            frame_info,
            # Texto inicial (\n = salto de línea).
            text="Dimensiones: ---\nPosición Inicio: ---\nTotal Víctimas: ---",
            # Fuente monoespaciada.
            font=("Consolas", 9)
        )
        # La coloca alineada a la izquierda.
        self.lbl_info_mapa.pack(anchor=tk.W)

    # Panel de estadísticas: caja de resumen individual + tabla comparativa de algoritmos.
    def _crear_panel_estadisticas_y_tabla(self, parent: ttk.Frame):
        """5. Panel de estadísticas y tabla comparativa exactamente como en el PDF."""
        # Marco con título para todo el bloque de resultados.
        frame_resultados = ttk.LabelFrame(parent, text="5. Estadísticas de Ejecución y Comparación", padding=10)
        # Ocupa ancho y alto, pero sin expandirse más allá de su tamaño natural (expand=False).
        frame_resultados.pack(fill=tk.BOTH, expand=False)

        # Contenedor horizontal: Tarjeta de Resumen Individual (Izquierda) | Tabla Comparativa (Derecha)
        # Fila que contendrá las dos zonas lado a lado.
        fila_stats = ttk.Frame(frame_resultados)
        # Se expande para llenar el marco.
        fila_stats.pack(fill=tk.BOTH, expand=True)

        # 1. Resumen Individual en formato caja
        # Caja "RESULTADO DE LA SIMULACIÓN".
        frame_caja_resumen = ttk.LabelFrame(fila_stats, text="RESULTADO DE LA SIMULACIÓN", padding=8)
        # La coloca a la izquierda, ocupando todo el alto, con 10 px de separación a la derecha.
        frame_caja_resumen.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Etiqueta con el resumen (inicia con "---" hasta que corra un algoritmo).
        self.lbl_resumen_detallado = ttk.Label(
            # Su contenedor.
            frame_caja_resumen,
            # Texto de 6 líneas, concatenando strings entre paréntesis.
            text=(
                # Línea 1: víctimas totales.
                "Víctimas totales    : ---\n"
                # Línea 2: rescatadas.
                "Víctimas rescatadas : ---\n"
                # Línea 3: fallecidas.
                "Víctimas fallecidas : ---\n"
                # Línea 4: ticks totales.
                "Ticks totales       : ---\n"
                # Línea 5: nodos expandidos.
                "Nodos expandidos    : ---\n"
                # Línea 6: tiempo de cómputo.
                "Tiempo de cómputo   : ---"
            ),
            # Fuente monoespaciada para que los ":" queden alineados.
            font=("Consolas", 9),
            # Alinea el texto multilínea a la izquierda.
            justify=tk.LEFT
        )
        # La coloca alineada a la izquierda.
        self.lbl_resumen_detallado.pack(anchor=tk.W)

        # 2. Tabla Comparativa de Algoritmos (Treeview)
        # Caja "COMPARACIÓN DE ALGORITMOS".
        frame_tabla = ttk.LabelFrame(fila_stats, text="COMPARACIÓN DE ALGORITMOS", padding=8)
        # La coloca a la izquierda (a continuación de la otra caja) y la deja crecer.
        frame_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Nombres internos de las 6 columnas de la tabla.
        columnas = ("algoritmo", "nodos", "tiempo", "rescatadas", "fallecidas", "ticks")
        # Crea la tabla (Treeview): solo muestra encabezados y filas (show="headings"), con 5 filas de alto.
        self.tree_comparacion = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=5)

        # Texto visible del encabezado de cada columna.
        self.tree_comparacion.heading("algoritmo", text="Algoritmo")
        # Encabezado de nodos.
        self.tree_comparacion.heading("nodos", text="Nodos")
        # Encabezado de tiempo.
        self.tree_comparacion.heading("tiempo", text="Tiempo")
        # Encabezado de rescatadas.
        self.tree_comparacion.heading("rescatadas", text="Rescatadas")
        # Encabezado de fallecidas.
        self.tree_comparacion.heading("fallecidas", text="Fallecidas")
        # Encabezado de ticks.
        self.tree_comparacion.heading("ticks", text="Ticks")

        # Ancho y alineación de cada columna (CENTER = centrado, E = derecha).
        self.tree_comparacion.column("algoritmo", width=85, anchor=tk.CENTER)
        # Nodos: alineado a la derecha.
        self.tree_comparacion.column("nodos", width=80, anchor=tk.E)
        # Tiempo: alineado a la derecha.
        self.tree_comparacion.column("tiempo", width=85, anchor=tk.E)
        # Rescatadas: centrado.
        self.tree_comparacion.column("rescatadas", width=85, anchor=tk.CENTER)
        # Fallecidas: centrado.
        self.tree_comparacion.column("fallecidas", width=85, anchor=tk.CENTER)
        # Ticks: centrado.
        self.tree_comparacion.column("ticks", width=65, anchor=tk.CENTER)

        # Coloca la tabla llenando su caja.
        self.tree_comparacion.pack(fill=tk.BOTH, expand=True)

    # Se ejecuta cada vez que se mueve el deslizador de velocidad; "val" llega como texto.
    def _actualizar_etiqueta_velocidad(self, val):
        # Convierte el valor a número decimal y luego a entero (milisegundos).
        ms = int(float(val))
        # Actualiza la etiqueta para mostrar, por ejemplo, "300 ms".
        self.lbl_vel_val.config(text=f"{ms} ms")

    # Se ejecuta al pulsar "Examinar..." del mapa.
    def _examinar_mapa(self):
        # Abre la ventana del sistema para elegir un archivo; devuelve la ruta elegida (o "" si se cancela).
        ruta = filedialog.askopenfilename(
            # Título de la ventana de selección.
            title="Seleccionar mapa.txt",
            # Filtros de tipo de archivo que muestra el diálogo.
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            # Carpeta inicial: la carpeta "data" relativa a donde se ejecuta el programa.
            initialdir=os.path.abspath("data")
        )
        # Si el usuario canceló (ruta vacía), no hace nada.
        if not ruta:
            return

        # Intenta cargar el mapa; si falla algo, se captura abajo.
        try:
            # Lee y valida el archivo; devuelve un objeto Mapa.
            mapa = cargar_mapa(ruta)
            # Guarda el mapa cargado.
            self.mapa = mapa
            # Guarda la ruta elegida.
            self.ruta_mapa = ruta
            # Muestra solo el nombre del archivo (sin toda la carpeta).
            self.lbl_ruta_mapa.config(text=os.path.basename(ruta))
            # Indicador verde de lectura correcta.
            self.lbl_estado_mapa.config(text="  [✓ Correcto]", foreground="#00AA00")
            # Refresca el panel de información (dimensiones, inicio, víctimas).
            self._actualizar_info()
            # Dibuja el mapa en el canvas.
            self._dibujar_mapa_estatico()
        # Si cualquier cosa falló (archivo inexistente, formato incorrecto, etc.)...
        except Exception as e:
            # Descarta el mapa.
            self.mapa = None
            # Indicador rojo de error.
            self.lbl_estado_mapa.config(text="  [✗ Error]", foreground="red")
            # Muestra un cuadro de error con el mensaje.
            messagebox.showerror("Error en Mapa", str(e))

    # Se ejecuta al pulsar "Examinar..." de víctimas.
    def _examinar_victimas(self):
        # Abre el diálogo de selección de archivo.
        ruta = filedialog.askopenfilename(
            # Título de la ventana.
            title="Seleccionar victimas.txt",
            # Acepta .txt y .csv.
            filetypes=[("Archivos de texto o CSV", "*.txt *.csv"), ("Todos los archivos", "*.*")],
            # Carpeta inicial "data".
            initialdir=os.path.abspath("data")
        )
        # Si se canceló, no hace nada.
        if not ruta:
            return

        # Intenta cargar las víctimas.
        try:
            # Lee y valida; si ya hay mapa cargado, también valida que las posiciones sean coherentes con él.
            victimas = cargar_victimas(ruta, mapa=self.mapa)
            # Guarda el diccionario de víctimas.
            self.victimas = victimas
            # Guarda la ruta elegida.
            self.ruta_victimas = ruta
            # Muestra el nombre del archivo.
            self.lbl_ruta_vic.config(text=os.path.basename(ruta))
            # Indicador verde de lectura correcta.
            self.lbl_estado_vic.config(text="  [✓ Correcto]", foreground="#00AA00")
            # Refresca el panel de información.
            self._actualizar_info()
            # Redibuja el mapa para que ya aparezcan las víctimas.
            self._dibujar_mapa_estatico()
        # Si algo falló...
        except Exception as e:
            # Descarta las víctimas.
            self.victimas = None
            # Indicador rojo de error.
            self.lbl_estado_vic.config(text="  [✗ Error]", foreground="red")
            # Muestra el cuadro de error.
            messagebox.showerror("Error en Víctimas", str(e))

    # Actualiza el texto del panel "Información del Mapa".
    def _actualizar_info(self):
        # Si hay mapa: texto con dimensiones e inicio; si no: guiones "---".
        txt_mapa = f"Dimensiones: {self.mapa.filas}x{self.mapa.columnas}\nInicio 'S': {self.mapa.inicio}" if self.mapa else "Dimensiones: ---\nInicio 'S': ---"
        # Si hay víctimas: muestra cuántas; si no: "---".
        txt_vic = f"\nTotal Víctimas: {len(self.victimas)}" if self.victimas else "\nTotal Víctimas: ---"
        # Junta ambos textos y los pone en la etiqueta.
        self.lbl_info_mapa.config(text=txt_mapa + txt_vic)

    # Dibuja TODO el mapa en el canvas (paredes, inicio, víctimas y agente). Se llama en cada tick de la animación.
    def _dibujar_mapa_estatico(self, pos_agente: Optional[Tuple[int, int]] = None, tick_actual: int = 0):
        # Si no hay mapa cargado, no hay nada que dibujar.
        if not self.mapa:
            return

        # Borra el dibujo anterior para redibujar desde cero.
        self.canvas.delete("all")
        # Ancho actual del canvas en píxeles.
        ancho_canvas = self.canvas.winfo_width()
        # Alto actual del canvas en píxeles.
        alto_canvas = self.canvas.winfo_height()

        # Si el canvas aún no tiene tamaño real (la ventana no terminó de dibujarse)...
        if ancho_canvas < 50 or alto_canvas < 50:
            # ...usa un tamaño por defecto para el ancho.
            ancho_canvas = 650
            # ...y para el alto.
            alto_canvas = 380

        # Margen interno de 20 px alrededor del mapa.
        margen = 20
        # Ancho disponible por celda si el mapa llenara el ancho.
        celda_w = (ancho_canvas - 2 * margen) / self.mapa.columnas
        # Alto disponible por celda si el mapa llenara el alto.
        celda_h = (alto_canvas - 2 * margen) / self.mapa.filas
        # Tamaño de celda cuadrada: el menor de ancho/alto/60, pero nunca menos de 18 px.
        tam_celda = max(18, min(celda_w, celda_h, 60))

        # Desplazamiento horizontal para centrar el mapa en el canvas.
        offset_x = (ancho_canvas - (tam_celda * self.mapa.columnas)) / 2
        # Desplazamiento vertical para centrar el mapa.
        offset_y = (alto_canvas - (tam_celda * self.mapa.filas)) / 2

        # Si no se indicó posición del agente, usa la posición inicial 'S'.
        if pos_agente is None:
            pos_agente = self.mapa.inicio

        # 1. Muros y Caminos
        # Recorre todas las filas del mapa.
        for r in range(self.mapa.filas):
            # Recorre todas las columnas de la fila.
            for c in range(self.mapa.columnas):
                # Esquina izquierda (x) de la celda.
                x1 = offset_x + c * tam_celda
                # Esquina superior (y) de la celda.
                y1 = offset_y + r * tam_celda
                # Esquina derecha (x).
                x2 = x1 + tam_celda
                # Esquina inferior (y).
                y2 = y1 + tam_celda

                # Carácter de esa celda en el mapa ('#', '.', 'S'...).
                caracter = self.mapa.celdas[r][c]
                # Si es pared...
                if caracter == '#':
                    # ...dibuja un rectángulo oscuro.
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#1F2421", outline="#34495E")
                # Si es cualquier otra cosa (camino libre o 'S')...
                else:
                    # ...dibuja un rectángulo claro.
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#ECEFF1", outline="#BDC3C7")

        # 2. Inicio 'S'
        # Fila y columna de la posición inicial.
        sr, sc = self.mapa.inicio
        # x de la esquina izquierda de la celda inicial.
        sx1 = offset_x + sc * tam_celda
        # y de la esquina superior de la celda inicial.
        sy1 = offset_y + sr * tam_celda
        # Escribe una "S" gris en el centro de esa celda.
        self.canvas.create_text(
            # Coordenadas del centro de la celda.
            sx1 + tam_celda / 2, sy1 + tam_celda / 2,
            # Texto, color y fuente (tamaño proporcional a la celda).
            text="S", fill="#7F8C8D", font=("Helvetica", int(tam_celda * 0.4), "bold")
        )

        # 3. Víctimas
        # Solo si ya se cargaron víctimas.
        if self.victimas:
            # Recorre cada objeto Victima.
            for v in self.victimas.values():
                # Esquina izquierda de la celda de la víctima.
                vx1 = offset_x + v.columna * tam_celda
                # Esquina superior.
                vy1 = offset_y + v.fila * tam_celda
                # Esquina derecha.
                vx2 = vx1 + tam_celda
                # Esquina inferior.
                vy2 = vy1 + tam_celda

                # Ticks que le quedan de vida a la víctima en el tick que se está mostrando.
                ticks_restantes = v.ticks_supervivencia - tick_actual

                # Si la animación ya la marcó como salvada...
                if v.id in self.victimas_salvadas_anim:
                    # ...color verde.
                    color_fondo = "#27AE60"
                    # ...texto con su id y "SALVADA".
                    texto_estado = f"{v.id}\n✓ SALVADA"
                # Si fue marcada muerta o ya no le quedan ticks (negativo)...
                elif v.id in self.victimas_muertas_anim or ticks_restantes < 0:
                    # ...color rojo.
                    color_fondo = "#E74C3C"
                    # ...texto con su id y "MUERTA".
                    texto_estado = f"{v.id}\n✗ MUERTA"
                # En cualquier otro caso, sigue viva.
                else:
                    # Color naranja.
                    color_fondo = "#F39C12"
                    # Texto con su id y el contador de ticks restantes.
                    texto_estado = f"{v.id}\n⏱ {ticks_restantes}"

                # Margen interno del círculo (8 % de la celda).
                pad = tam_celda * 0.08
                # Dibuja el óvalo (círculo) de la víctima con borde blanco.
                self.canvas.create_oval(vx1 + pad, vy1 + pad, vx2 - pad, vy2 - pad, fill=color_fondo, outline="#FFFFFF", width=2)
                # Escribe el texto de estado en el centro del círculo.
                self.canvas.create_text(
                    # Centro de la celda.
                    vx1 + tam_celda / 2, vy1 + tam_celda / 2,
                    # Texto y color blanco.
                    text=texto_estado, fill="#FFFFFF",
                    # Fuente proporcional a la celda (mínimo 7).
                    font=("Helvetica", max(7, int(tam_celda * 0.22)), "bold"),
                    # Centra las dos líneas del texto.
                    justify=tk.CENTER
                )

        # 4. Agente
        # Fila y columna actuales del agente.
        ar, ac = pos_agente
        # Esquina izquierda de la celda del agente.
        ax1 = offset_x + ac * tam_celda
        # Esquina superior.
        ay1 = offset_y + ar * tam_celda
        # Esquina derecha.
        ax2 = ax1 + tam_celda
        # Esquina inferior.
        ay2 = ay1 + tam_celda

        # Margen interno del cuadro del agente (15 % de la celda).
        pad_agente = tam_celda * 0.15
        # Dibuja el cuadro azul del agente con borde amarillo (se dibuja al final para quedar encima).
        self.canvas.create_rectangle(
            # Coordenadas del rectángulo con el margen aplicado.
            ax1 + pad_agente, ay1 + pad_agente, ax2 - pad_agente, ay2 - pad_agente,
            # Relleno azul, borde amarillo de 3 px.
            fill="#2980B9", outline="#F1C40F", width=3
        )
        # Escribe "AGENTE" en el centro de su cuadro.
        self.canvas.create_text(
            # Centro de la celda.
            ax1 + tam_celda / 2, ay1 + tam_celda / 2,
            # Texto blanco.
            text="AGENTE", fill="#FFFFFF",
            # Fuente proporcional (mínimo 7).
            font=("Helvetica", max(7, int(tam_celda * 0.2)), "bold")
        )

    # Se ejecuta al pulsar "Iniciar Rescate": corre el algoritmo elegido y arranca la animación.
    def _iniciar_rescate(self):
        # Si no hay mapa cargado, avisa y termina.
        if not self.mapa:
            messagebox.showwarning("Falta Mapa", "Por favor cargue un archivo de mapa válido primero.")
            return
        # Si no hay víctimas cargadas, avisa y termina.
        if not self.victimas:
            messagebox.showwarning("Faltan Víctimas", "Por favor cargue un archivo de víctimas válido primero.")
            return

        # Si había un temporizador de animación pendiente...
        if self.after_id:
            # ...lo cancela para que no haya dos animaciones a la vez.
            self.root.after_cancel(self.after_id)
            # Limpia el identificador.
            self.after_id = None

        # Lee el algoritmo seleccionado en el menú desplegable.
        algoritmo = self.combo_algoritmo.get()

        # Si eligió A*, ejecuta A*.
        if algoritmo == "A*":
            resultado = busqueda_a_estrella(self.mapa, self.victimas)
        # Si eligió BFS, ejecuta Amplitud.
        elif algoritmo == "BFS":
            resultado = busqueda_amplitud(self.mapa, self.victimas)
        # Si eligió UCS, ejecuta Costo Uniforme.
        elif algoritmo == "UCS":
            resultado = busqueda_costo_uniforme(self.mapa, self.victimas)
        # Si eligió IDDFS, ejecuta Profundidad Iterativa con cota máxima de 16.
        elif algoritmo == "IDDFS":
            resultado = busqueda_profundidad_iterativa(self.mapa, self.victimas, limite_maximo_cota=16)
        # Cualquier otro valor (no debería pasar): no hace nada.
        else:
            return

        # Guarda el resultado para que la animación lo use.
        self.resultado_actual = resultado

        # Actualizar panel de resumen individual
        # Muestra los números del resultado en la caja de resumen.
        self._actualizar_panel_resumen_individual(resultado)

        # Agregar o actualizar la fila de este algoritmo en la tabla comparativa
        # Inserta/actualiza la fila de este algoritmo en la tabla.
        self._actualizar_fila_tabla(resultado)

        # Preparar y lanzar animación
        # Empieza desde el paso 0 (estado inicial).
        self.paso_actual = 0
        # Marca la animación como activa.
        self.animacion_activa = True
        # Y no pausada.
        self.animacion_pausada = False
        # Borra el registro de víctimas salvadas de una animación anterior.
        self.victimas_salvadas_anim.clear()
        # Borra el registro de víctimas muertas de una animación anterior.
        self.victimas_muertas_anim.clear()

        # Habilita el botón Pausar (con su texto original).
        self.btn_pausa.config(state=tk.NORMAL, text="⏸ Pausar")
        # Habilita el botón Reiniciar.
        self.btn_reiniciar.config(state=tk.NORMAL)
        # Deshabilita "Iniciar" mientras corre la animación.
        self.btn_iniciar.config(state=tk.DISABLED)

        # Dibuja el primer cuadro; los siguientes se programan solos.
        self._siguiente_paso_animacion()

    # Dibuja UN paso (tick) de la animación y se reprograma para el siguiente.
    def _siguiente_paso_animacion(self):
        # Si la animación no está activa o está pausada, no hace nada.
        if not self.animacion_activa or self.animacion_pausada:
            return

        # Si no hay resultado o la ruta está vacía, no hay nada que animar.
        if not self.resultado_actual or not self.resultado_actual.camino:
            return

        # Lista de pasos (accion, fila, columna) del resultado.
        camino = self.resultado_actual.camino
        # Si todavía quedan pasos por mostrar...
        if self.paso_actual < len(camino):
            # Toma la acción y la posición del paso actual.
            accion, r, c = camino[self.paso_actual]
            # El número de paso coincide con el tick (paso 0 = tick 0).
            tick = self.paso_actual
            # Actualiza la etiqueta superior con el tick y la acción ("Inicio" si no hay acción).
            self.lbl_tick_actual.config(text=f"Tick: {tick} ({accion if accion else 'Inicio'})")

            # Actualiza qué víctimas están salvadas o muertas en este tick.
            for v in self.victimas.values():
                # Si ya estaba marcada como salvada, se salta.
                if v.id in self.victimas_salvadas_anim:
                    continue
                # Si el agente está justo en la celda de esta víctima...
                if v.fila == r and v.columna == c:
                    # ...y llegó a tiempo (tick <= límite)...
                    if tick <= v.ticks_supervivencia:
                        # ...la marca como salvada.
                        self.victimas_salvadas_anim.add(v.id)
                # Si el agente no está en su celda...
                else:
                    # ...y el tick ya superó su límite de supervivencia...
                    if tick > v.ticks_supervivencia:
                        # ...la marca como muerta.
                        self.victimas_muertas_anim.add(v.id)

            # Redibuja el mapa con el agente en su nueva posición y los contadores actualizados.
            self._dibujar_mapa_estatico(pos_agente=(r, c), tick_actual=tick)

            # Avanza al siguiente paso para la próxima llamada.
            self.paso_actual += 1
            # Lee la velocidad elegida (ms entre ticks) del deslizador.
            delay = int(self.scale_velocidad.get())
            # Programa esta misma función para ejecutarse de nuevo tras "delay" ms; guarda el id para poder cancelarlo.
            self.after_id = self.root.after(delay, self._siguiente_paso_animacion)
        # Si ya se mostraron todos los pasos...
        else:
            # Marca la animación como terminada.
            self.animacion_activa = False
            # Vuelve a habilitar "Iniciar Rescate".
            self.btn_iniciar.config(state=tk.NORMAL)
            # Deshabilita "Pausar" porque ya no hay animación.
            self.btn_pausa.config(state=tk.DISABLED)

    # Escribe los resultados del algoritmo en la caja de resumen individual.
    def _actualizar_panel_resumen_individual(self, res: ResultadoBusqueda):
        """Actualiza la caja de resumen individual con el formato del PDF."""
        # Arma el texto de 6 líneas con los valores del resultado.
        texto = (
            # Total de víctimas.
            f"Víctimas totales    : {res.victimas_totales}\n"
            # Rescatadas con marca ✓.
            f"Víctimas rescatadas : {res.rescatadas}  (✓)\n"
            # Fallecidas con marca ✗.
            f"Víctimas fallecidas : {res.fallecidas}  (✗)\n"
            # Ticks totales de la ruta.
            f"Ticks totales       : {res.ticks_totales}\n"
            # Nodos expandidos por el algoritmo.
            f"Nodos expandidos    : {res.nodos_expandidos}\n"
            # Tiempo con 4 decimales.
            f"Tiempo de cómputo   : {res.tiempo_segundos:.4f}s"
        )
        # Pone el texto en la etiqueta.
        self.lbl_resumen_detallado.config(text=texto)

    # Agrega (o reemplaza) la fila de un algoritmo en la tabla comparativa.
    def _actualizar_fila_tabla(self, res: ResultadoBusqueda):
        """Inserta o actualiza la fila de un algoritmo en la tabla comparativa."""
        # Verificar si ya existe en la tabla para actualizarlo
        # Recorre las filas existentes de la tabla.
        for item in self.tree_comparacion.get_children():
            # Si la primera columna (nombre del algoritmo) coincide con el del resultado...
            if self.tree_comparacion.item(item, "values")[0] == res.algoritmo:
                # ...borra esa fila vieja (se insertará la nueva abajo).
                self.tree_comparacion.delete(item)

        # Valores de la nueva fila, todos convertidos a texto.
        valores = (
            # Nombre del algoritmo.
            res.algoritmo,
            # Nodos expandidos.
            str(res.nodos_expandidos),
            # Tiempo con 4 decimales y "s".
            f"{res.tiempo_segundos:.4f}s",
            # Víctimas rescatadas.
            str(res.rescatadas),
            # Víctimas fallecidas.
            str(res.fallecidas),
            # Ticks totales.
            str(res.ticks_totales)
        )
        # Inserta la fila al final de la tabla ("" = sin padre; tk.END = al final).
        self.tree_comparacion.insert("", tk.END, values=valores)

    # Se ejecuta al pulsar "Comparar los 4 Algoritmos": corre todos y llena la tabla (sin animación).
    def _comparar_todos_los_algoritmos(self):
        """Ejecuta los 4 algoritmos secuencialmente y llena la tabla completa."""
        # Si falta el mapa o las víctimas, avisa y termina.
        if not self.mapa or not self.victimas:
            messagebox.showwarning("Datos Requeridos", "Debe cargar el mapa y las víctimas antes de comparar.")
            return

        # Limpiar tabla
        # Borra todas las filas actuales de la tabla.
        for item in self.tree_comparacion.get_children():
            self.tree_comparacion.delete(item)

        # Ejecutar los 4 algoritmos
        # Lista de funciones a ejecutar, en el orden en que aparecerán en la tabla.
        algoritmos_funcs = [
            # BFS.
            busqueda_amplitud,
            # UCS.
            busqueda_costo_uniforme,
            # IDDFS: se envuelve en una función lambda para poder pasarle la cota máxima de 16.
            lambda m, v: busqueda_profundidad_iterativa(m, v, limite_maximo_cota=16),
            # A*.
            busqueda_a_estrella
        ]

        # Recorre cada función de la lista.
        for func in algoritmos_funcs:
            # La ejecuta con el mapa y las víctimas cargadas.
            resultado = func(self.mapa, self.victimas)
            # Agrega su fila a la tabla.
            self._actualizar_fila_tabla(resultado)

        # Avisa que terminó con un cuadro informativo.
        messagebox.showinfo(
            # Título del cuadro.
            "Comparación Exitosa",
            # Mensaje del cuadro.
            "Los 4 algoritmos fueron ejecutados y comparados con éxito en la tabla inferior."
        )

    # Se ejecuta al pulsar Pausar/Reanudar (el mismo botón alterna).
    def _pausar_animacion(self):
        # Si ya estaba pausada → reanudar.
        if self.animacion_pausada:
            # Quita la marca de pausa.
            self.animacion_pausada = False
            # Cambia el texto del botón de vuelta a "Pausar".
            self.btn_pausa.config(text="⏸ Pausar")
            # Retoma la animación dibujando el siguiente paso.
            self._siguiente_paso_animacion()
        # Si estaba corriendo → pausar.
        else:
            # Marca la pausa.
            self.animacion_pausada = True
            # Cambia el texto del botón a "Reanudar".
            self.btn_pausa.config(text="▶ Reanudar")
            # Si hay un temporizador pendiente...
            if self.after_id:
                # ...lo cancela para que no se dibuje el siguiente paso.
                self.root.after_cancel(self.after_id)
                # Limpia el identificador.
                self.after_id = None

    # Se ejecuta al pulsar Reiniciar: detiene la animación y vuelve al estado inicial de la vista.
    def _reiniciar_animacion(self):
        # Si hay un temporizador pendiente, lo cancela.
        if self.after_id:
            self.root.after_cancel(self.after_id)
            # Limpia el identificador.
            self.after_id = None

        # La animación deja de estar activa.
        self.animacion_activa = False
        # Y no está pausada.
        self.animacion_pausada = False
        # Vuelve al paso 0.
        self.paso_actual = 0
        # Olvida las víctimas marcadas como salvadas.
        self.victimas_salvadas_anim.clear()
        # Olvida las víctimas marcadas como muertas.
        self.victimas_muertas_anim.clear()

        # Deshabilita Pausar y restaura su texto.
        self.btn_pausa.config(state=tk.DISABLED, text="⏸ Pausar")
        # Deshabilita Reiniciar.
        self.btn_reiniciar.config(state=tk.DISABLED)
        # Habilita Iniciar Rescate.
        self.btn_iniciar.config(state=tk.NORMAL)
        # Reinicia el contador visual de ticks.
        self.lbl_tick_actual.config(text="Tick: 0")

        # Redibuja el mapa en su estado inicial.
        self._dibujar_mapa_estatico()


# Función de arranque (duplicada de main.py, permite ejecutar este archivo directamente).
def main():
    # Crea la ventana raíz.
    root = tk.Tk()
    # Crea la aplicación sobre esa ventana.
    app = AppRescate(root)
    # Inicia el bucle de eventos de Tkinter.
    root.mainloop()


# Solo se ejecuta si este archivo se corre directamente.
if __name__ == "__main__":
    # Lanza la aplicación.
    main()