"""
Módulo de funciones heurísticas para el algoritmo A* (Tarjeta 3.1).
Demostración de admisibilidad incluida en la documentación de cada función.
"""

from typing import Dict, Tuple
from src.models import Estado, Victima
from src.evaluator import distancia_manhattan


def heuristica_victimas_condenadas(estado: Estado, dict_victimas: Dict[str, Victima]) -> int:
    """
    Heurística Admisible Base propuesta en el enunciado del proyecto:
    h(n) = número de víctimas vivas que ya están matemáticamente condenadas a morir.

    Demostración de Admisibilidad:
    - Una víctima v está condenada si distancia_Manhattan(agente, v) > ticks_restantes(v).
    - Dado que distancia_Manhattan es la distancia mínima en línea recta sin obstáculos,
      cualquier ruta real con paredes tendrá distancia_real >= distancia_Manhattan.
    - Por tanto, si distancia_Manhattan > ticks_restantes, entonces distancia_real > ticks_restantes,
      lo que significa que la víctima morirá con 100% de certeza.
    - Como nunca cuenta muertes que no ocurrirán, h(n) <= h*(n) en todos los estados.
    - Por definición, h(n) es ADMISIBLE.
    """
    pos_agente = (estado.fila, estado.columna)
    condenadas = 0

    for id_v in estado.victimas_vivas:
        v = dict_victimas[id_v]
        ticks_restantes = v.ticks_supervivencia - estado.tick_actual

        if ticks_restantes < 0:
            condenadas += 1
            continue

        distancia = distancia_manhattan(pos_agente, (v.fila, v.columna))
        if distancia > ticks_restantes:
            condenadas += 1

    return condenadas


def heuristica_a_estrella(estado: Estado, dict_victimas: Dict[str, Victima]) -> Tuple[int, int]:
    """
    Heurística compuesta para guiar eficientemente la cola de prioridad en A*.
    Retorna una tupla de dos valores:
    1. victimas_perdidas_estimadas:
       (víctimas ya fallecidas) + (víctimas actualmente condenadas por distancia Manhattan).
    2. distancia_minima_alcanzable:
       Distancia Manhattan hacia la víctima alcanzable más cercana (para romper empates
       y atraer al agente hacia el siguiente rescate con el menor rodeo posible).
    """
    pos_agente = (estado.fila, estado.columna)
    victimas_totales = len(dict_victimas)
    
    condenadas = 0
    distancia_minima = 0
    distancias_alcanzables = []

    for id_v in estado.victimas_vivas:
        v = dict_victimas[id_v]
        ticks_restantes = v.ticks_supervivencia - estado.tick_actual

        if ticks_restantes < 0:
            condenadas += 1
            continue

        dist = distancia_manhattan(pos_agente, (v.fila, v.columna))
        if dist > ticks_restantes:
            condenadas += 1
        else:
            distancias_alcanzables.append(dist)

    if distancias_alcanzables:
        distancia_minima = min(distancias_alcanzables)

    # Víctimas que ya murieron antes de este estado
    ya_fallecidas = victimas_totales - len(estado.victimas_rescatadas) - len(estado.victimas_vivas)
    total_perdidas = ya_fallecidas + condenadas

    return total_perdidas, distancia_minima

