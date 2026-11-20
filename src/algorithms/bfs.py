"""
Implementación del algoritmo de Búsqueda en Amplitud (BFS) desde cero.
Sin librerías externas.
"""

import time
from collections import deque
from typing import Dict, List, Optional
from src.models import Mapa, Victima, Estado
from src.evaluator import es_estado_objetivo, es_mejor_solucion
from src.distancias import calcular_tabla_distancias

class ResultadoBusqueda:
    """
    Estructura de datos estándar para almacenar las métricas y la solución
    encontrada por cualquier algoritmo de búsqueda.
    """
    def __init__(
        self,
        algoritmo: str,
        estado_final: Optional[Estado],
        nodos_expandidos: int,
        tiempo_segundos: float,
        victimas_totales: int
    ):
        self.algoritmo = algoritmo
        self.estado_final = estado_final
        self.nodos_expandidos = nodos_expandidos
        self.tiempo_segundos = tiempo_segundos
        self.victimas_totales = victimas_totales

        if estado_final is not None:
            self.rescatadas = len(estado_final.victimas_rescatadas)
            self.fallecidas = victimas_totales - self.rescatadas
            self.ticks_totales = estado_final.tick_actual
            self.camino = estado_final.reconstruir_camino()
        else:
            self.rescatadas = 0
            self.fallecidas = victimas_totales
            self.ticks_totales = 0
            self.camino = []

    def __repr__(self) -> str:
        return (
            f"[{self.algoritmo}] Nodos: {self.nodos_expandidos} | "
            f"Tiempo: {self.tiempo_segundos:.4f}s | "
            f"Rescatadas: {self.rescatadas}/{self.victimas_totales} | "
            f"Fallecidas: {self.fallecidas} | "
            f"Ticks: {self.ticks_totales}"
        )


def busqueda_amplitud(mapa: Mapa, dict_victimas: Dict[str, Victima]) -> ResultadoBusqueda:
    """
    Ejecuta el algoritmo de Búsqueda en Amplitud (BFS).
    
    1. Utiliza una cola FIFO (deque).
    2. Registra las CLAVES de estado visitadas (posición, vivas, rescatadas; sin tick).
       BFS expande por tick creciente, así que la primera vez que se llega a una
       clave es con el menor tick: cualquier llegada posterior está dominada.
    3. Busca la ruta que maximice las víctimas rescatadas.
    4. Mide tiempo de cómputo y nodos expandidos.
    """
    tiempo_inicio = time.perf_counter()
    nodos_expandidos = 0
    victimas_totales = len(dict_victimas)

    # Distancias reales (solo para el predicado de meta: "¿hay víctimas alcanzables?")
    tabla = calcular_tabla_distancias(mapa, dict_victimas)

    # Estado Inicial: Agente en 'S', todas las víctimas vivas, tick = 0
    estado_inicial = Estado(
        fila=mapa.inicio[0],
        columna=mapa.inicio[1],
        victimas_vivas=frozenset(dict_victimas.keys()),
        tick_actual=0,
        victimas_rescatadas=frozenset()
    )

    # Cola FIFO de exploración (Frontier)
    cola = deque([estado_inicial])
    
    # Conjunto cerrado de estados visitados (evita ciclos)
    visitados = {estado_inicial.clave()}

    mejor_solucion: Optional[Estado] = None

    while cola:
        estado_actual = cola.popleft()
        nodos_expandidos += 1

        # ¿Es un estado terminal/objetivo? (No quedan víctimas alcanzables)
        if es_estado_objetivo(estado_actual, dict_victimas, tabla):
            if es_mejor_solucion(candidato=estado_actual, actual_mejor=mejor_solucion):
                mejor_solucion = estado_actual
                # Si ya rescatamos a TODAS las víctimas posibles en el mapa, es la solución óptima absoluta
                if len(mejor_solucion.victimas_rescatadas) == victimas_totales:
                    break
            # Como ya no hay víctimas vivas alcanzables en esta rama, no tiene sentido expandirla
            continue

        # Si aún hay esperanza de rescatar víctimas, generamos los sucesores
        for sucesor in estado_actual.generar_sucesores(mapa, dict_victimas):
            if sucesor.clave() not in visitados:
                visitados.add(sucesor.clave())
                cola.append(sucesor)

    tiempo_total = time.perf_counter() - tiempo_inicio

    return ResultadoBusqueda(
        algoritmo="BFS",
        estado_final=mejor_solucion,
        nodos_expandidos=nodos_expandidos,
        tiempo_segundos=tiempo_total,
        victimas_totales=victimas_totales
    )