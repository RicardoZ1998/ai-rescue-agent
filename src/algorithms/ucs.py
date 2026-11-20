"""
Implementación del algoritmo de Búsqueda de Costo Uniforme (UCS / Dijkstra) desde cero.
Sin librerías externas.
"""

# Módulo para medir tiempo.
import time
# heapq = cola de prioridad (min-heap) de la biblioteca estándar; siempre saca el elemento más pequeño.
import heapq
# Tipos para anotaciones.
from typing import Dict, Optional
# Clases propias del problema.
from src.models import Mapa, Victima, Estado
# Funciones de evaluación: criterio de parada y comparador de soluciones.
from src.evaluator import es_estado_objetivo, es_mejor_solucion
# Reutiliza la clase de resultado definida en bfs.py.
from src.algorithms.bfs import ResultadoBusqueda


# Función principal de UCS.
def busqueda_costo_uniforme(mapa: Mapa, dict_victimas: Dict[str, Victima]) -> ResultadoBusqueda:
    """
    Ejecuta el algoritmo de Búsqueda de Costo Uniforme (UCS).
    
    1. Utiliza una cola de prioridad Min-Heap (heapq).
    2. El costo acumulado g(n) corresponde al número de ticks transcurridos (tick_actual).
    3. Desempate seguro usando un contador secuencial para evitar errores con heapq.
    4. Mantiene un diccionario de mejores costos conocidos g(n) por estado.
    5. Mide tiempo de cómputo y nodos expandidos.
    """
    # Marca el instante de inicio.
    tiempo_inicio = time.perf_counter()
    # Contador de nodos expandidos.
    nodos_expandidos = 0
    # Total de víctimas del problema.
    victimas_totales = len(dict_victimas)
    # Contador secuencial que sirve de desempate en el heap (para no comparar objetos Estado entre sí).
    contador_orden = 0

    # Estado Inicial: Agente en 'S', todas las víctimas vivas, tick = 0
    estado_inicial = Estado(
        # Fila de 'S'.
        fila=mapa.inicio[0],
        # Columna de 'S'.
        columna=mapa.inicio[1],
        # Todas las víctimas vivas.
        victimas_vivas=frozenset(dict_victimas.keys()),
        # Tick 0.
        tick_actual=0,
        # Ninguna rescatada.
        victimas_rescatadas=frozenset()
    )

    # Cola de prioridad (Min-Heap): tuplas (costo_g, contador_secuencial, estado)
    # La frontera es una lista vacía que heapq manejará como heap.
    frontera = []
    # Inserta el estado inicial con costo 0 y contador 0.
    heapq.heappush(frontera, (0, contador_orden, estado_inicial))

    # Diccionario de costo mínimo conocido para alcanzar cada estado
    # El estado inicial cuesta 0.
    costos_minimos = {estado_inicial: 0}

    # Mejor solución terminal encontrada hasta ahora.
    mejor_solucion: Optional[Estado] = None

    # Mientras haya nodos en la frontera...
    while frontera:
        # Saca el nodo de menor costo g (desempata por el contador); "_" ignora el contador.
        costo_g, _, estado_actual = heapq.heappop(frontera)
        # Cuenta el nodo como expandido.
        nodos_expandidos += 1

        # Si encontramos un camino más barato a este estado posteriormente, descartamos este
        # Esta entrada es "vieja" (ya se registró un costo menor para el mismo estado): se ignora.
        if costo_g > costos_minimos.get(estado_actual, float('inf')):
            continue

        # ¿Es un estado terminal/objetivo? (No quedan víctimas alcanzables)
        if es_estado_objetivo(estado_actual, dict_victimas):
            # ¿Es mejor que la mejor solución guardada?
            if es_mejor_solucion(candidato=estado_actual, actual_mejor=mejor_solucion):
                # Actualiza la mejor solución.
                mejor_solucion = estado_actual
                # Si ya rescatamos a TODAS las víctimas posibles en el mapa, es óptimo
                if len(mejor_solucion.victimas_rescatadas) == victimas_totales:
                    # Parada anticipada: rescatar a todas es lo mejor posible.
                    break
            # Como ya no hay víctimas vivas alcanzables en esta rama, no expandimos más
            # Pasa al siguiente nodo sin generar sucesores.
            continue

        # Generar sucesores en 4 direcciones
        for sucesor in estado_actual.generar_sucesores(mapa, dict_victimas):
            # El costo de llegar al sucesor es su tick (cada paso cuesta 1, así g = ticks transcurridos).
            nuevo_costo = sucesor.tick_actual

            # Solo lo agrega si es la primera vez que se ve o si llegó con un costo menor al conocido.
            if nuevo_costo < costos_minimos.get(sucesor, float('inf')):
                # Registra el nuevo mejor costo para ese estado.
                costos_minimos[sucesor] = nuevo_costo
                # Incrementa el contador de desempate.
                contador_orden += 1
                # Inserta en el heap la tupla (costo, desempate, estado).
                heapq.heappush(frontera, (nuevo_costo, contador_orden, sucesor))

    # Tiempo total transcurrido.
    tiempo_total = time.perf_counter() - tiempo_inicio

    # Empaqueta y devuelve el resultado.
    return ResultadoBusqueda(
        # Nombre para la tabla.
        algoritmo="UCS",
        # Mejor estado terminal.
        estado_final=mejor_solucion,
        # Nodos expandidos.
        nodos_expandidos=nodos_expandidos,
        # Tiempo en segundos.
        tiempo_segundos=tiempo_total,
        # Total de víctimas.
        victimas_totales=victimas_totales
    )