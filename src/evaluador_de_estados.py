from typing import Tuple, Dict
from src.modelos_de_datos import EstadoDelAgente, VictimaEnRiesgo

def calcular_distancia_manhattan(posicion_origen: Tuple[int, int], posicion_destino: Tuple[int, int]) -> int:
    return abs(posicion_origen[0] - posicion_destino[0]) + abs(posicion_origen[1] - posicion_destino[1])


def es_victima_alcanzable(posicion_del_agente: Tuple[int, int], tick_actual: int, victima: VictimaEnRiesgo) -> bool:
    ticks_de_vida_restantes_de_la_victima = victima.ticks_supervivencia - tick_actual
    if ticks_de_vida_restantes_de_la_victima < 0:
        return False
    
    distancia_manhattan_calculada = calcular_distancia_manhattan(posicion_del_agente, (victima.fila, victima.columna))
    return distancia_manhattan_calculada <= ticks_de_vida_restantes_de_la_victima


def es_estado_objetivo(estado: EstadoDelAgente, diccionario_de_victimas: Dict[str, VictimaEnRiesgo]) -> bool:
    if len(estado.victimas_vivas) == 0:
        return True

    posicion_actual_del_agente = (estado.fila, estado.columna)
    
    for identificador_de_victima in estado.victimas_vivas:
        victima_siendo_evaluada = diccionario_de_victimas[identificador_de_victima]
        if es_victima_alcanzable(posicion_actual_del_agente, estado.tick_actual, victima_siendo_evaluada):
            return False

    return True


def es_mejor_solucion(estado_candidato: EstadoDelAgente, actual_mejor_estado: EstadoDelAgente) -> bool:
    if actual_mejor_estado is None:
        return True

    cantidad_rescatadas_por_el_candidato = len(estado_candidato.victimas_rescatadas)
    cantidad_rescatadas_por_el_actual_mejor = len(actual_mejor_estado.victimas_rescatadas)

    if cantidad_rescatadas_por_el_candidato > cantidad_rescatadas_por_el_actual_mejor:
        return True
    
    if cantidad_rescatadas_por_el_candidato == cantidad_rescatadas_por_el_actual_mejor:
        return estado_candidato.tick_actual < actual_mejor_estado.tick_actual

    return False

