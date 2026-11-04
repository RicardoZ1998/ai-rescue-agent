from typing import Dict, Tuple
from src.modelos_de_datos import EstadoDelAgente, VictimaEnRiesgo
from src.evaluador_de_estados import calcular_distancia_manhattan


def calcular_heuristica_de_victimas_condenadas(estado: EstadoDelAgente, diccionario_de_victimas: Dict[str, VictimaEnRiesgo]) -> int:
    posicion_actual_del_agente = (estado.fila, estado.columna)
    cantidad_de_victimas_condenadas = 0

    for identificador_de_victima in estado.victimas_vivas:
        victima_evaluada = diccionario_de_victimas[identificador_de_victima]
        ticks_de_vida_restantes = victima_evaluada.ticks_supervivencia - estado.tick_actual

        if ticks_de_vida_restantes < 0:
            cantidad_de_victimas_condenadas += 1
            continue

        distancia_manhattan_hacia_la_victima = calcular_distancia_manhattan(posicion_actual_del_agente, (victima_evaluada.fila, victima_evaluada.columna))
        if distancia_manhattan_hacia_la_victima > ticks_de_vida_restantes:
            cantidad_de_victimas_condenadas += 1

    return cantidad_de_victimas_condenadas


def calcular_heuristica_para_busqueda_a_estrella(estado: EstadoDelAgente, diccionario_de_victimas: Dict[str, VictimaEnRiesgo]) -> Tuple[int, int]:
    posicion_actual_del_agente = (estado.fila, estado.columna)
    cantidad_total_de_victimas = len(diccionario_de_victimas)
    
    cantidad_de_victimas_condenadas = 0
    distancia_minima_hacia_victima_alcanzable = 0
    lista_de_distancias_a_victimas_alcanzables = []

    for identificador_de_victima in estado.victimas_vivas:
        victima_evaluada = diccionario_de_victimas[identificador_de_victima]
        ticks_de_vida_restantes = victima_evaluada.ticks_supervivencia - estado.tick_actual

        if ticks_de_vida_restantes < 0:
            cantidad_de_victimas_condenadas += 1
            continue

        distancia_manhattan_hacia_la_victima = calcular_distancia_manhattan(posicion_actual_del_agente, (victima_evaluada.fila, victima_evaluada.columna))
        if distancia_manhattan_hacia_la_victima > ticks_de_vida_restantes:
            cantidad_de_victimas_condenadas += 1
        else:
            lista_de_distancias_a_victimas_alcanzables.append(distancia_manhattan_hacia_la_victima)

    if lista_de_distancias_a_victimas_alcanzables:
        distancia_minima_hacia_victima_alcanzable = min(lista_de_distancias_a_victimas_alcanzables)

    cantidad_de_victimas_ya_fallecidas = cantidad_total_de_victimas - len(estado.victimas_rescatadas) - len(estado.victimas_vivas)
    total_de_victimas_perdidas_estimadas = cantidad_de_victimas_ya_fallecidas + cantidad_de_victimas_condenadas

    return total_de_victimas_perdidas_estimadas, distancia_minima_hacia_victima_alcanzable

