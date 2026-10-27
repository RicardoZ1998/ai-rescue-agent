"""
Módulo para evaluación de estados, criterios de parada y calidad de soluciones (Tarjeta 1.3).
Sin librerías externas.
"""

from typing import Tuple, Dict
from src.models import Estado, Victima

def distancia_manhattan(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """
    Calcula la distancia Manhattan (L1) entre dos coordenadas (fila, col):
    |r1 - r2| + |c1 - c2|
    Representa la distancia mínima teórica en una cuadrícula sin obstáculos.
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def es_victima_alcanzable(pos_agente: Tuple[int, int], tick_actual: int, victima: Victima) -> bool:
    """
    Determina si una víctima aún puede ser rescatada teóricamente.
    Una víctima es INALCANZABLE si la distancia mínima en línea recta (Manhattan)
    es mayor a los ticks que le quedan de vida.
    """
    ticks_restantes = victima.ticks_supervivencia - tick_actual
    if ticks_restantes < 0:
        return False
    
    distancia = distancia_manhattan(pos_agente, (victima.fila, victima.columna))
    return distancia <= ticks_restantes


def es_estado_objetivo(estado: Estado, dict_victimas: Dict[str, Victima]) -> bool:
    """
    Criterio formal de parada:
    Un estado es OBJETIVO si no existe ninguna víctima viva alcanzable
    (todas fueron rescatadas o las que quedan vivas están condenadas a morir).
    """
    # Si no queda ninguna víctima viva en el mapa, es objetivo
    if len(estado.victimas_vivas) == 0:
        return True

    pos_agente = (estado.fila, estado.columna)
    
    # Si queda alguna víctima viva, verificar si al menos una es alcanzable
    for id_v in estado.victimas_vivas:
        victima = dict_victimas[id_v]
        if es_victima_alcanzable(pos_agente, estado.tick_actual, victima):
            # Todavía hay esperanza de salvar a esta víctima: NO es estado terminal
            return False

    # Ninguna de las víctimas vivas restantes puede ser alcanzada a tiempo
    return True


def es_mejor_solucion(candidato: Estado, actual_mejor: Estado) -> bool:
    """
    Determina si un estado solución 'candidato' es estrictamente mejor que 'actual_mejor'.
    
    Criterios de calificación:
    1. Maximizar víctimas rescatadas (criterio principal).
    2. Minimizar ticks totales en caso de empate en víctimas rescatadas (criterio de desempate).
    """
    if actual_mejor is None:
        return True

    rescatadas_candidato = len(candidato.victimas_rescatadas)
    rescatadas_actual = len(actual_mejor.victimas_rescatadas)

    # 1. Mayor número de víctimas rescatadas
    if rescatadas_candidato > rescatadas_actual:
        return True
    
    # 2. Desempate: Menor número de ticks (más rápido)
    if rescatadas_candidato == rescatadas_actual:
        return candidato.tick_actual < actual_mejor.tick_actual

    return False
