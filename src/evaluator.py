"""
Módulo para evaluación de estados, criterios de parada y calidad de soluciones (Tarjeta 1.3).
Sin librerías externas.
"""

# Tipos para anotaciones: Tuple (posiciones) y Dict (diccionario de víctimas).
from typing import Tuple, Dict
# Clases propias: Estado (nodo de búsqueda) y Victima.
from src.models import Estado, Victima

# Distancia Manhattan entre dos celdas: pasos mínimos si no hubiera paredes.
def distancia_manhattan(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """
    Calcula la distancia Manhattan (L1) entre dos coordenadas (fila, col):
    |r1 - r2| + |c1 - c2|
    Representa la distancia mínima teórica en una cuadrícula sin obstáculos.
    """
    # abs() da el valor absoluto: suma la diferencia de filas y la diferencia de columnas.
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


# ¿Aún se podría llegar a tiempo a esta víctima? (comprobación optimista, ignora paredes)
def es_victima_alcanzable(pos_agente: Tuple[int, int], tick_actual: int, victima: Victima) -> bool:
    """
    Determina si una víctima aún puede ser rescatada teóricamente.
    Una víctima es INALCANZABLE si la distancia mínima en línea recta (Manhattan)
    es mayor a los ticks que le quedan de vida.
    """
    # Ticks que le quedan de vida = su límite menos el tick en que va la simulación.
    ticks_restantes = victima.ticks_supervivencia - tick_actual
    # Si ya es negativo, ya murió: no es alcanzable.
    if ticks_restantes < 0:
        return False
    
    # Distancia mínima teórica desde el agente hasta la víctima.
    distancia = distancia_manhattan(pos_agente, (victima.fila, victima.columna))
    # Alcanzable si la distancia cabe dentro de los ticks que le quedan.
    return distancia <= ticks_restantes


# Criterio de parada: decide si un estado es terminal (ya no vale la pena seguir expandiéndolo).
def es_estado_objetivo(estado: Estado, dict_victimas: Dict[str, Victima]) -> bool:
    """
    Criterio formal de parada:
    Un estado es OBJETIVO si no existe ninguna víctima viva alcanzable
    (todas fueron rescatadas o las que quedan vivas están condenadas a morir).
    """
    # Si no queda ninguna víctima viva en el mapa, es objetivo
    # Sin vivas, no hay nada más que rescatar: estado terminal.
    if len(estado.victimas_vivas) == 0:
        return True

    # Posición del agente como tupla (fila, columna).
    pos_agente = (estado.fila, estado.columna)
    
    # Si queda alguna víctima viva, verificar si al menos una es alcanzable
    # Revisa cada víctima viva.
    for id_v in estado.victimas_vivas:
        # Obtiene el objeto Victima por su id.
        victima = dict_victimas[id_v]
        # Si esta víctima aún es alcanzable (según Manhattan y su tiempo)...
        if es_victima_alcanzable(pos_agente, estado.tick_actual, victima):
            # Todavía hay esperanza de salvar a esta víctima: NO es estado terminal
            return False

    # Ninguna de las víctimas vivas restantes puede ser alcanzada a tiempo
    # Ninguna era alcanzable: es estado terminal.
    return True


# Compara dos estados terminales y dice si "candidato" es mejor que "actual_mejor".
def es_mejor_solucion(candidato: Estado, actual_mejor: Estado) -> bool:
    """
    Determina si un estado solución 'candidato' es estrictamente mejor que 'actual_mejor'.
    
    Criterios de calificación:
    1. Maximizar víctimas rescatadas (criterio principal).
    2. Minimizar ticks totales en caso de empate en víctimas rescatadas (criterio de desempate).
    """
    # Si todavía no hay mejor solución guardada, cualquier candidato gana.
    if actual_mejor is None:
        return True

    # Cantidad de víctimas rescatadas por el candidato.
    rescatadas_candidato = len(candidato.victimas_rescatadas)
    # Cantidad de víctimas rescatadas por la mejor solución actual.
    rescatadas_actual = len(actual_mejor.victimas_rescatadas)

    # 1. Mayor número de víctimas rescatadas
    # El candidato rescata más: es mejor.
    if rescatadas_candidato > rescatadas_actual:
        return True
    
    # 2. Desempate: Menor número de ticks (más rápido)
    # Si rescatan lo mismo, gana el que usó menos ticks (comparación estricta "<").
    if rescatadas_candidato == rescatadas_actual:
        return candidato.tick_actual < actual_mejor.tick_actual

    # El candidato rescata menos: no es mejor.
    return False