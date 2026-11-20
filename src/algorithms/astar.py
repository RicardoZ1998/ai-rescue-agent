"""
Implementación del algoritmo de Búsqueda Informada A* desde cero.
Sin librerías externas.
"""

import time
import heapq
from typing import Dict, Optional
from src.models import Mapa, Victima, Estado
from src.evaluator import es_estado_objetivo, es_mejor_solucion
from src.heuristics import heuristica_a_estrella
from src.algorithms.bfs import ResultadoBusqueda
from src.distancias import calcular_tabla_distancias


def busqueda_a_estrella(mapa: Mapa, dict_victimas: Dict[str, Victima]) -> ResultadoBusqueda:
    """
    Ejecuta el algoritmo de Búsqueda Informada A*.
    
    1. Utiliza una cola de prioridad Min-Heap (heapq).
    2. Función de evaluación f(n) guiada por:
       - f_perdidas = víctimas que ya murieron + víctimas condenadas h(n)
       - f_distancia = distancia Manhattan hacia la víctima alcanzable más cercana
       - g_cost = ticks acumulados
    3. Poda estricta de ramas subóptimas contra la mejor cota encontrada.
    4. Mide tiempo de cómputo y nodos expandidos.
    """
    tiempo_inicio = time.perf_counter()
    nodos_expandidos = 0
    # Distancias reales por BFS (respetan paredes): heurística más informada que Manhattan
    tabla = calcular_tabla_distancias(mapa, dict_victimas)
    victimas_totales = len(dict_victimas)
    contador_orden = 0

    estado_inicial = Estado(
        fila=mapa.inicio[0],
        columna=mapa.inicio[1],
        victimas_vivas=frozenset(dict_victimas.keys()),
        tick_actual=0,
        victimas_rescatadas=frozenset()
    )

    perdidas_h, dist_min_h = heuristica_a_estrella(estado_inicial, dict_victimas, tabla)
    
    # Cola de prioridad: (perdidas_f, dist_min_h, tick_g, contador, estado)
    frontera = []
    heapq.heappush(frontera, (perdidas_h, dist_min_h, 0, contador_orden, estado_inicial))

    costos_g = {estado_inicial.clave(): 0}  # clave (sin tick) -> menor g conocido
    mejor_solucion: Optional[Estado] = None

    while frontera:
        perdidas_f, dist_f, g_actual, _, estado_actual = heapq.heappop(frontera)
        nodos_expandidos += 1

        # Poda por cota: Si este estado ya no puede mejorar a la mejor solución actual
        if mejor_solucion is not None:
            perdidas_mejor = victimas_totales - len(mejor_solucion.victimas_rescatadas)
            if perdidas_f > perdidas_mejor:
                continue
            if perdidas_f == perdidas_mejor and g_actual >= mejor_solucion.tick_actual:
                continue

        # Si ya conocemos una ruta con menor g a este estado, descartamos esta
        if g_actual > costos_g.get(estado_actual.clave(), float('inf')):
            continue

        # ¿Es un estado terminal/objetivo?
        if es_estado_objetivo(estado_actual, dict_victimas, tabla):
            if es_mejor_solucion(candidato=estado_actual, actual_mejor=mejor_solucion):
                mejor_solucion = estado_actual
                if len(mejor_solucion.victimas_rescatadas) == victimas_totales:
                    break
            continue

        # Generar sucesores en 4 direcciones
        for sucesor in estado_actual.generar_sucesores(mapa, dict_victimas):
            nuevo_g = sucesor.tick_actual
            perdidas_suc, dist_suc = heuristica_a_estrella(sucesor, dict_victimas, tabla)

            # Poda temprana si el sucesor ya no puede superar la mejor solución
            if mejor_solucion is not None:
                perdidas_mejor = victimas_totales - len(mejor_solucion.victimas_rescatadas)
                if perdidas_suc > perdidas_mejor:
                    continue
                if perdidas_suc == perdidas_mejor and nuevo_g >= mejor_solucion.tick_actual:
                    continue

            if nuevo_g < costos_g.get(sucesor.clave(), float('inf')):
                costos_g[sucesor.clave()] = nuevo_g
                contador_orden += 1
                heapq.heappush(
                    frontera,
                    (perdidas_suc, dist_suc, nuevo_g, contador_orden, sucesor)
                )

    tiempo_total = time.perf_counter() - tiempo_inicio

    return ResultadoBusqueda(
        algoritmo="A*",
        estado_final=mejor_solucion,
        nodos_expandidos=nodos_expandidos,
        tiempo_segundos=tiempo_total,
        victimas_totales=victimas_totales
    )