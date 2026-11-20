"""
Implementación del algoritmo de Búsqueda en Profundidad Iterativa (IDDFS) desde cero.
Sin librerías externas.
"""

import time
from typing import Dict, Optional, Tuple
from src.models import Mapa, Victima, Estado
from src.evaluator import es_estado_objetivo, es_mejor_solucion
from src.distancias import calcular_tabla_distancias
from src.algorithms.bfs import ResultadoBusqueda


def _dls_recursivo(
    estado: Estado,
    limite: int,
    mapa: Mapa,
    dict_victimas: Dict[str, Victima],
    vistos: Dict[Tuple, int],
    tabla,
    contador_nodos: list,
    mejor_solucion: list,
    victimas_totales: int
) -> bool:
    """
    Depth-Limited Search (DLS) recursivo.
    - vistos: tabla de transposición {clave_de_estado: menor tick con que se alcanzó}
      en la iteración actual. Si se vuelve a llegar a la misma clave con un tick
      mayor o igual, ese camino está dominado y se descarta. Como la profundidad
      coincide con el tick, esto también evita ciclos (volver a la misma celda con
      las mismas víctimas vivas siempre ocurre en un tick mayor).
    - contador_nodos: lista con un entero mutable para contar expansiones acumuladas.
    - mejor_solucion: lista de 1 elemento [mejor_estado] para actualizar por referencia.
    Retorna True si encontró la solución óptima absoluta (todas las víctimas rescatadas).
    """
    contador_nodos[0] += 1

    # Evaluar si el estado es objetivo (no quedan víctimas alcanzables)
    if es_estado_objetivo(estado, dict_victimas, tabla):
        if es_mejor_solucion(candidato=estado, actual_mejor=mejor_solucion[0]):
            mejor_solucion[0] = estado
            if len(mejor_solucion[0].victimas_rescatadas) == victimas_totales:
                return True  # Parada temprana: todas las víctimas rescatadas
        return False

    # Si alcanzamos el límite de profundidad para esta iteración, no descendemos más
    if estado.tick_actual >= limite:
        return False

    # Poda por cota trivial (NO usa heurística, solo cuenta): lo máximo que esta rama
    # puede lograr es rescatadas + vivas. Si no puede superar a la mejor solución
    # (ni empatarla en menos ticks), no vale la pena seguir.
    mejor = mejor_solucion[0]
    if mejor is not None:
        potencial = len(estado.victimas_rescatadas) + len(estado.victimas_vivas)
        rescatadas_mejor = len(mejor.victimas_rescatadas)
        if potencial < rescatadas_mejor:
            return False
        if potencial == rescatadas_mejor and estado.tick_actual >= mejor.tick_actual:
            return False

    # Explorar sucesores en profundidad (DFS)
    for sucesor in estado.generar_sucesores(mapa, dict_victimas):
        clave = sucesor.clave()
        if clave in vistos and vistos[clave] <= sucesor.tick_actual:
            continue  # Dominado: ya se llegó aquí igual o más rápido
        vistos[clave] = sucesor.tick_actual

        if _dls_recursivo(
            estado=sucesor,
            limite=limite,
            mapa=mapa,
            dict_victimas=dict_victimas,
            vistos=vistos,
            tabla=tabla,
            contador_nodos=contador_nodos,
            mejor_solucion=mejor_solucion,
            victimas_totales=victimas_totales
        ):
            return True

    return False


def busqueda_profundidad_iterativa(
    mapa: Mapa,
    dict_victimas: Dict[str, Victima],
    limite_maximo_cota: Optional[int] = None
) -> ResultadoBusqueda:
    """
    Ejecuta el algoritmo de Búsqueda en Profundidad Iterativa (IDDFS).

    1. Itera incrementando el límite de profundidad L (en ticks) desde 0.
    2. En cada iteración ejecuta DLS (Depth-Limited Search).
    3. Acumula los nodos expandidos totales entre todas las iteraciones.
    4. La profundidad máxima natural es max(ticks_supervivencia) + 1: en ese tick
       todas las víctimas ya murieron, así que no existen estados más profundos
       que valga la pena visitar. Por eso NO se necesita un tope arbitrario.
       `limite_maximo_cota` es opcional y solo sirve para forzar un tope menor
       (si se usa, el resultado puede dejar de ser óptimo).
    """
    tiempo_inicio = time.perf_counter()
    nodos_expandidos = [0]
    victimas_totales = len(dict_victimas)

    # Distancias reales (solo para el predicado de meta)
    tabla = calcular_tabla_distancias(mapa, dict_victimas)

    estado_inicial = Estado(
        fila=mapa.inicio[0],
        columna=mapa.inicio[1],
        victimas_vivas=frozenset(dict_victimas.keys()),
        tick_actual=0,
        victimas_rescatadas=frozenset()
    )

    max_tick_victimas = max((v.ticks_supervivencia for v in dict_victimas.values()), default=0)
    cota_profundidad = max_tick_victimas + 1
    if limite_maximo_cota is not None:
        cota_profundidad = min(limite_maximo_cota, cota_profundidad)

    mejor_solucion = [None]

    for limite in range(cota_profundidad + 1):
        vistos = {estado_inicial.clave(): 0}  # tabla de transposición, nueva en cada iteración
        terminar_absoluto = _dls_recursivo(
            estado=estado_inicial,
            limite=limite,
            mapa=mapa,
            dict_victimas=dict_victimas,
            vistos=vistos,
            tabla=tabla,
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