"""
Implementación del algoritmo de Búsqueda de Costo Uniforme (UCS / Dijkstra) desde cero.
Sin librerías externas.
"""

import time
import heapq
from typing import Dict, Optional
from src.models import Mapa, Victima, Estado
from src.evaluator import es_estado_objetivo, es_mejor_solucion
from src.algorithms.bfs import ResultadoBusqueda


def busqueda_costo_uniforme(mapa: Mapa, dict_victimas: Dict[str, Victima]) -> ResultadoBusqueda:
    """
    Ejecuta el algoritmo de Búsqueda de Costo Uniforme (UCS).
    
    1. Utiliza una cola de prioridad Min-Heap (heapq).
    2. El costo acumulado g(n) corresponde al número de ticks transcurridos (tick_actual).
    3. Desempate seguro usando un contador secuencial para evitar errores con heapq.
    4. Mantiene un diccionario de mejores costos conocidos g(n) por estado.
    5. Mide tiempo de cómputo y nodos expandidos.
    """
    tiempo_inicio = time.perf_counter()
    nodos_expandidos = 0
    victimas_totales = len(dict_victimas)
    contador_orden = 0

    # Estado Inicial: Agente en 'S', todas las víctimas vivas, tick = 0
    estado_inicial = Estado(
        fila=mapa.inicio[0],
        columna=mapa.inicio[1],
        victimas_vivas=frozenset(dict_victimas.keys()),
        tick_actual=0,
        victimas_rescatadas=frozenset()
    )

    # Cola de prioridad (Min-Heap): tuplas (costo_g, contador_secuencial, estado)
    frontera = []
    heapq.heappush(frontera, (0, contador_orden, estado_inicial))

    # Diccionario de costo mínimo conocido para alcanzar cada estado
    costos_minimos = {estado_inicial: 0}

    mejor_solucion: Optional[Estado] = None

    while frontera:
        costo_g, _, estado_actual = heapq.heappop(frontera)
        nodos_expandidos += 1

        # Si encontramos un camino más barato a este estado posteriormente, descartamos este
        if costo_g > costos_minimos.get(estado_actual, float('inf')):
            continue

        # ¿Es un estado terminal/objetivo? (No quedan víctimas alcanzables)
        if es_estado_objetivo(estado_actual, dict_victimas):
            if es_mejor_solucion(candidato=estado_actual, actual_mejor=mejor_solucion):
                mejor_solucion = estado_actual
                # Si ya rescatamos a TODAS las víctimas posibles en el mapa, es óptimo
                if len(mejor_solucion.victimas_rescatadas) == victimas_totales:
                    break
            # Como ya no hay víctimas vivas alcanzables en esta rama, no expandimos más
            continue

        # Generar sucesores en 4 direcciones
        for sucesor in estado_actual.generar_sucesores(mapa, dict_victimas):
            nuevo_costo = sucesor.tick_actual

            if nuevo_costo < costos_minimos.get(sucesor, float('inf')):
                costos_minimos[sucesor] = nuevo_costo
                contador_orden += 1
                heapq.heappush(frontera, (nuevo_costo, contador_orden, sucesor))

    tiempo_total = time.perf_counter() - tiempo_inicio

    return ResultadoBusqueda(
        algoritmo="UCS",
        estado_final=mejor_solucion,
        nodos_expandidos=nodos_expandidos,
        tiempo_segundos=tiempo_total,
        victimas_totales=victimas_totales
    )

