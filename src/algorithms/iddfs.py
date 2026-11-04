"""
Implementación del algoritmo de Búsqueda en Profundidad Iterativa (IDDFS) desde cero.
Sin librerías externas.
"""

import time
from typing import Dict, Optional, Tuple, Set
from src.models import Mapa, Victima, Estado
from src.evaluator import es_estado_objetivo, es_mejor_solucion
from src.algorithms.bfs import ResultadoBusqueda


def _dls_recursivo(
    estado: Estado,
    limite: int,
    mapa: Mapa,
    dict_victimas: Dict[str, Victima],
    ruta_actual: Set[Estado],
    contador_nodos: list,
    mejor_solucion: list,
    victimas_totales: int
) -> bool:
    """
    Depth-Limited Search (DLS) recursivo.
    - ruta_actual: conjunto de estados en la rama activa para evitar ciclos locales.
    - contador_nodos: lista con un entero mutable para contar expansiones acumuladas.
    - mejor_solucion: lista de 1 elemento [mejor_estado] para actualizar por referencia.
    Retorna True si encontró la solución óptima absoluta (todas las víctimas rescatadas).
    """
    contador_nodos[0] += 1

    # Evaluar si el estado es objetivo (no quedan víctimas alcanzables)
    if es_estado_objetivo(estado, dict_victimas):
        if es_mejor_solucion(candidato=estado, actual_mejor=mejor_solucion[0]):
            mejor_solucion[0] = estado
            if len(mejor_solucion[0].victimas_rescatadas) == victimas_totales:
                return True  # Parada temprana: todas las víctimas rescatadas
        return False

    # Si alcanzamos el límite de profundidad para esta iteración, no descendemos más
    if estado.tick_actual >= limite:
        return False

    # Explorar sucesores en profundidad (DFS)
    for sucesor in estado.generar_sucesores(mapa, dict_victimas):
        if sucesor not in ruta_actual:
            ruta_actual.add(sucesor)
            encontro_optimo = _dls_recursivo(
                estado=sucesor,
                limite=limite,
                mapa=mapa,
                dict_victimas=dict_victimas,
                ruta_actual=ruta_actual,
                contador_nodos=contador_nodos,
                mejor_solucion=mejor_solucion,
                victimas_totales=victimas_totales
            )
            ruta_actual.remove(sucesor)  # Backtracking

            if encontro_optimo:
                return True

    return False


def busqueda_profundidad_iterativa(
    mapa: Mapa,
    dict_victimas: Dict[str, Victima],
    limite_maximo_cota: int = 50
) -> ResultadoBusqueda:
    """
    Ejecuta el algoritmo de Búsqueda en Profundidad Iterativa (IDDFS).
    
    1. Itera incrementando el límite de profundidad L desde 0 hasta la cota máxima.
    2. En cada iteración ejecuta DLS (Depth-Limited Search).
    3. Acumula los nodos expandidos totales entre todas las iteraciones.
    4. Garantiza encontrar la ruta con menor número de ticks para el mejor rescate.
    """
    tiempo_inicio = time.perf_counter()
    nodos_expandidos = [0]
    victimas_totales = len(dict_victimas)

    estado_inicial = Estado(
        fila=mapa.inicio[0],
        columna=mapa.inicio[1],
        victimas_vivas=frozenset(dict_victimas.keys()),
        tick_actual=0,
        victimas_rescatadas=frozenset()
    )

    # Determinar la cota máxima de ticks razonable basada en las víctimas
    # Ninguna víctima vive más allá del máximo ticks_supervivencia
    max_tick_victimas = max((v.ticks_supervivencia for v in dict_victimas.values()), default=0)
    cota_profundidad = min(limite_maximo_cota, max_tick_victimas + 5)

    mejor_solucion = [None]

    for limite in range(cota_profundidad + 1):
        ruta_actual = {estado_inicial}
        terminar_absoluto = _dls_recursivo(
            estado=estado_inicial,
            limite=limite,
            mapa=mapa,
            dict_victimas=dict_victimas,
            ruta_actual=ruta_actual,
            contador_nodos=nodos_expandidos,
            mejor_solucion=mejor_solucion,
            victimas_totales=victimas_totales
        )
        if terminar_absoluto:
            break

    tiempo_total = time.perf_counter() - tiempo_inicio

    return ResultadoBusqueda(
        algoritmo="IDDFS",
        estado_final=mejor_solucion[0],
        nodos_expandidos=nodos_expandidos[0],
        tiempo_segundos=tiempo_total,
        victimas_totales=victimas_totales
    )

