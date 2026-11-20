"""
Implementación del algoritmo de Búsqueda en Amplitud (BFS) desde cero.
Sin librerías externas.
"""

# Módulo estándar para medir tiempo (se usa time.perf_counter()).
import time
# deque = cola de doble extremo; permite sacar del frente (popleft) en tiempo constante, ideal para FIFO.
from collections import deque
# Tipos para anotaciones (Optional = "puede ser None").
from typing import Dict, List, Optional
# Clases propias del problema.
from src.models import Mapa, Victima, Estado
# Funciones de evaluación: criterio de parada y comparador de soluciones.
from src.evaluator import es_estado_objetivo, es_mejor_solucion

# Clase contenedora del resultado de cualquier algoritmo (también la usan UCS, IDDFS y A*).
class ResultadoBusqueda:
    """
    Estructura de datos estándar para almacenar las métricas y la solución
    encontrada por cualquier algoritmo de búsqueda.
    """
    # Constructor: recibe lo que midió el algoritmo y calcula el resto.
    def __init__(
        self,
        # Nombre del algoritmo ("BFS", "UCS", "IDDFS", "A*").
        algoritmo: str,
        # Mejor estado terminal encontrado (o None si no se encontró ninguno).
        estado_final: Optional[Estado],
        # Cuántos nodos sacó el algoritmo de la frontera/expandió.
        nodos_expandidos: int,
        # Tiempo de cómputo en segundos.
        tiempo_segundos: float,
        # Número total de víctimas del problema.
        victimas_totales: int
    ):
        # Guarda el nombre del algoritmo.
        self.algoritmo = algoritmo
        # Guarda el estado final.
        self.estado_final = estado_final
        # Guarda la cantidad de nodos expandidos.
        self.nodos_expandidos = nodos_expandidos
        # Guarda el tiempo de ejecución.
        self.tiempo_segundos = tiempo_segundos
        # Guarda el total de víctimas.
        self.victimas_totales = victimas_totales

        # Si el algoritmo sí encontró un estado final...
        if estado_final is not None:
            # Rescatadas = tamaño del conjunto de rescatadas del estado final.
            self.rescatadas = len(estado_final.victimas_rescatadas)
            # Fallecidas = totales - rescatadas.
            self.fallecidas = victimas_totales - self.rescatadas
            # Ticks totales = tick en el que quedó el estado final.
            self.ticks_totales = estado_final.tick_actual
            # Camino = lista de pasos (acción, fila, columna) desde el inicio hasta el estado final.
            self.camino = estado_final.reconstruir_camino()
        # Si no se encontró solución...
        else:
            # No se rescató a nadie.
            self.rescatadas = 0
            # Todas se cuentan como fallecidas.
            self.fallecidas = victimas_totales
            # Sin movimientos.
            self.ticks_totales = 0
            # Sin camino.
            self.camino = []

    # Texto de resumen del resultado (útil para imprimir en consola/pruebas).
    def __repr__(self) -> str:
        # Une varios fragmentos en un solo texto con formato.
        return (
            # Algoritmo y nodos expandidos.
            f"[{self.algoritmo}] Nodos: {self.nodos_expandidos} | "
            # Tiempo con 4 decimales.
            f"Tiempo: {self.tiempo_segundos:.4f}s | "
            # Rescatadas sobre el total.
            f"Rescatadas: {self.rescatadas}/{self.victimas_totales} | "
            # Fallecidas.
            f"Fallecidas: {self.fallecidas} | "
            # Ticks totales.
            f"Ticks: {self.ticks_totales}"
        )


# Función principal de BFS.
def busqueda_amplitud(mapa: Mapa, dict_victimas: Dict[str, Victima]) -> ResultadoBusqueda:
    """
    Ejecuta el algoritmo de Búsqueda en Amplitud (BFS).
    
    1. Utiliza una cola FIFO (deque).
    2. Registra los estados visitados en un set para evitar ciclos.
    3. Busca la ruta que maximice las víctimas rescatadas.
    4. Mide tiempo de cómputo y nodos expandidos.
    """
    # Marca el instante de inicio para medir cuánto tarda el algoritmo.
    tiempo_inicio = time.perf_counter()
    # Contador de nodos expandidos, arranca en 0.
    nodos_expandidos = 0
    # Número total de víctimas (se usa para saber si ya se rescataron todas).
    victimas_totales = len(dict_victimas)

    # Estado Inicial: Agente en 'S', todas las víctimas vivas, tick = 0
    estado_inicial = Estado(
        # Fila de la posición inicial 'S'.
        fila=mapa.inicio[0],
        # Columna de la posición inicial 'S'.
        columna=mapa.inicio[1],
        # Todas las víctimas empiezan vivas (conjunto con todos los ids).
        victimas_vivas=frozenset(dict_victimas.keys()),
        # Empieza en el tick 0.
        tick_actual=0,
        # Nadie rescatado todavía.
        victimas_rescatadas=frozenset()
    )

    # Cola FIFO de exploración (Frontier)
    # La frontera arranca con el estado inicial.
    cola = deque([estado_inicial])
    
    # Conjunto cerrado de estados visitados (evita ciclos)
    # Se marca el estado inicial como visitado.
    visitados = set([estado_inicial])

    # Aquí se guardará la mejor solución terminal encontrada hasta el momento.
    mejor_solucion: Optional[Estado] = None

    # Mientras haya nodos por explorar en la frontera...
    while cola:
        # Saca el nodo más antiguo de la cola (FIFO = amplitud: se exploran todos los de un nivel antes del siguiente).
        estado_actual = cola.popleft()
        # Cuenta este nodo como expandido.
        nodos_expandidos += 1

        # ¿Es un estado terminal/objetivo? (No quedan víctimas alcanzables)
        if es_estado_objetivo(estado_actual, dict_victimas):
            # Si es mejor que la mejor solución guardada (más rescatadas, o igual y menos ticks)...
            if es_mejor_solucion(candidato=estado_actual, actual_mejor=mejor_solucion):
                # ...la guarda como la nueva mejor.
                mejor_solucion = estado_actual
                # Si ya rescatamos a TODAS las víctimas posibles en el mapa, es la solución óptima absoluta
                if len(mejor_solucion.victimas_rescatadas) == victimas_totales:
                    # Parada anticipada: no se puede mejorar más que rescatar a todos.
                    break
            # Como ya no hay víctimas vivas alcanzables en esta rama, no tiene sentido expandirla
            # Salta al siguiente nodo de la cola sin generar sucesores.
            continue

        # Si aún hay esperanza de rescatar víctimas, generamos los sucesores
        # Genera los estados hijos (hasta 4 movimientos válidos).
        for sucesor in estado_actual.generar_sucesores(mapa, dict_victimas):
            # Solo agrega el sucesor si no se había visto antes (evita repetir estados idénticos).
            if sucesor not in visitados:
                # Lo marca como visitado.
                visitados.add(sucesor)
                # Lo encola al final de la frontera.
                cola.append(sucesor)

    # Mide cuánto tiempo pasó desde el inicio.
    tiempo_total = time.perf_counter() - tiempo_inicio

    # Empaqueta todo en un ResultadoBusqueda y lo devuelve.
    return ResultadoBusqueda(
        # Nombre que se mostrará en la tabla.
        algoritmo="BFS",
        # Mejor estado terminal encontrado (o None).
        estado_final=mejor_solucion,
        # Nodos expandidos en total.
        nodos_expandidos=nodos_expandidos,
        # Tiempo de ejecución en segundos.
        tiempo_segundos=tiempo_total,
        # Total de víctimas del problema.
        victimas_totales=victimas_totales
    )