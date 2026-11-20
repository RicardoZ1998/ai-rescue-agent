"""
Implementación del algoritmo de Búsqueda Informada A* desde cero.
Sin librerías externas.
"""

# Módulo para medir tiempo.
import time
# heapq = cola de prioridad (min-heap).
import heapq
# Tipos para anotaciones.
from typing import Dict, Optional
# Clases propias del problema.
from src.models import Mapa, Victima, Estado
# Funciones de evaluación: criterio de parada y comparador de soluciones.
from src.evaluator import es_estado_objetivo, es_mejor_solucion
# Heurística compuesta (pérdidas estimadas, distancia mínima).
from src.heuristics import heuristica_a_estrella
# Reutiliza la clase de resultado definida en bfs.py.
from src.algorithms.bfs import ResultadoBusqueda


# Función principal de A*.
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
    # Marca el instante de inicio.
    tiempo_inicio = time.perf_counter()
    # Contador de nodos expandidos.
    nodos_expandidos = 0
    # Total de víctimas del problema.
    victimas_totales = len(dict_victimas)
    # Contador secuencial de desempate para el heap.
    contador_orden = 0

    # Estado inicial: agente en 'S', todas vivas, tick 0, ninguna rescatada.
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

    # Calcula la heurística del estado inicial: (pérdidas estimadas, distancia mínima a una alcanzable).
    perdidas_h, dist_min_h = heuristica_a_estrella(estado_inicial, dict_victimas)
    
    # Cola de prioridad: (perdidas_f, dist_min_h, tick_g, contador, estado)
    # Lista vacía que heapq usará como heap.
    frontera = []
    # Inserta el estado inicial. El heap ordena por: 1) pérdidas, 2) distancia, 3) g (ticks), 4) contador.
    heapq.heappush(frontera, (perdidas_h, dist_min_h, 0, contador_orden, estado_inicial))

    # Mejor g (ticks) conocido para cada estado; el inicial tiene g = 0.
    costos_g = {estado_inicial: 0}
    # Mejor solución terminal encontrada hasta ahora.
    mejor_solucion: Optional[Estado] = None

    # Mientras haya nodos en la frontera...
    while frontera:
        # Saca el nodo con menor prioridad (la tupla se compara de izquierda a derecha).
        perdidas_f, dist_f, g_actual, _, estado_actual = heapq.heappop(frontera)
        # Cuenta el nodo como expandido.
        nodos_expandidos += 1

        # Poda por cota: Si este estado ya no puede mejorar a la mejor solución actual
        # Solo se poda si ya existe una solución guardada.
        if mejor_solucion is not None:
            # Pérdidas de la mejor solución actual = totales - rescatadas.
            perdidas_mejor = victimas_totales - len(mejor_solucion.victimas_rescatadas)
            # Si este nodo ya garantiza más pérdidas que la mejor solución, se descarta.
            if perdidas_f > perdidas_mejor:
                continue
            # Si garantiza las mismas pérdidas pero ya gastó igual o más ticks, tampoco puede mejorarla.
            if perdidas_f == perdidas_mejor and g_actual >= mejor_solucion.tick_actual:
                continue

        # Si ya conocemos una ruta con menor g a este estado, descartamos esta
        # Esta entrada es "vieja" (hay un camino más barato registrado): se ignora.
        if g_actual > costos_g.get(estado_actual, float('inf')):
            continue

        # ¿Es un estado terminal/objetivo?
        if es_estado_objetivo(estado_actual, dict_victimas):
            # ¿Es mejor que la mejor solución guardada?
            if es_mejor_solucion(candidato=estado_actual, actual_mejor=mejor_solucion):
                # Actualiza la mejor solución.
                mejor_solucion = estado_actual
                # Si ya rescató a todas las víctimas, es el óptimo absoluto: termina.
                if len(mejor_solucion.victimas_rescatadas) == victimas_totales:
                    break
            # Estado terminal: no se expande más.
            continue

        # Generar sucesores en 4 direcciones
        for sucesor in estado_actual.generar_sucesores(mapa, dict_victimas):
            # g del sucesor = su tick (cada paso cuesta 1).
            nuevo_g = sucesor.tick_actual
            # Heurística del sucesor: (pérdidas estimadas, distancia mínima a una víctima alcanzable).
            perdidas_suc, dist_suc = heuristica_a_estrella(sucesor, dict_victimas)

            # Poda temprana si el sucesor ya no puede superar la mejor solución
            # Solo si ya hay una solución guardada.
            if mejor_solucion is not None:
                # Pérdidas de la mejor solución actual.
                perdidas_mejor = victimas_totales - len(mejor_solucion.victimas_rescatadas)
                # Si el sucesor ya garantiza más pérdidas, no se agrega a la frontera.
                if perdidas_suc > perdidas_mejor:
                    continue
                # Si garantiza las mismas pérdidas pero no es más rápido, tampoco.
                if perdidas_suc == perdidas_mejor and nuevo_g >= mejor_solucion.tick_actual:
                    continue

            # Solo se agrega si es la primera vez que se ve o si llegó con menor g que antes.
            if nuevo_g < costos_g.get(sucesor, float('inf')):
                # Registra el mejor g del sucesor.
                costos_g[sucesor] = nuevo_g
                # Incrementa el contador de desempate.
                contador_orden += 1
                # Inserta el sucesor en el heap con su tupla de prioridad.
                heapq.heappush(
                    # Heap/frontera.
                    frontera,
                    # (pérdidas estimadas, distancia, g, desempate, estado)
                    (perdidas_suc, dist_suc, nuevo_g, contador_orden, sucesor)
                )

    # Tiempo total transcurrido.
    tiempo_total = time.perf_counter() - tiempo_inicio

    # Empaqueta y devuelve el resultado.
    return ResultadoBusqueda(
        # Nombre para la tabla.
        algoritmo="A*",
        # Mejor estado terminal.
        estado_final=mejor_solucion,
        # Nodos expandidos.
        nodos_expandidos=nodos_expandidos,
        # Tiempo en segundos.
        tiempo_segundos=tiempo_total,
        # Total de víctimas.
        victimas_totales=victimas_totales
    )