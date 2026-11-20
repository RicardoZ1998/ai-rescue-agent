"""
Módulo de distancias reales sobre el mapa (respetando paredes).

Se calcula UNA sola vez por problema con un BFS desde la celda de cada víctima.
Como el movimiento es simétrico (4 direcciones, costo 1), la distancia
víctima -> celda es igual a la distancia celda -> víctima.

Uso:
    - Predicado de meta ("¿alguna víctima viva es realmente alcanzable?").
    - Heurística de A* (distancia real >= Manhattan, por lo tanto sigue siendo
      admisible y es más informada).
"""

from collections import deque
from typing import Dict, Tuple
from src.models import Mapa, Victima

Tabla = Dict[str, Dict[Tuple[int, int], int]]


def calcular_tabla_distancias(mapa: Mapa, dict_victimas: Dict[str, Victima]) -> Tabla:
    """
    Retorna {id_victima: {(fila, col): distancia_real_en_pasos}}.
    Las celdas que no aparecen en el diccionario son INALCANZABLES para esa víctima
    (por ejemplo, si está encerrada o si la víctima está sobre una pared).
    """
    tabla: Tabla = {}
    for id_v, v in dict_victimas.items():
        distancias: Dict[Tuple[int, int], int] = {}
        origen = (v.fila, v.columna)

        if mapa.es_posicion_valida(*origen):
            distancias[origen] = 0
            cola = deque([origen])
            while cola:
                f, c = cola.popleft()
                for df, dc in ((-1, 0), (1, 0), (0, 1), (0, -1)):
                    vecino = (f + df, c + dc)
                    if vecino not in distancias and mapa.es_posicion_valida(*vecino):
                        distancias[vecino] = distancias[(f, c)] + 1
                        cola.append(vecino)

        tabla[id_v] = distancias
    return tabla