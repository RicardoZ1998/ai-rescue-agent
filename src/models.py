"""
Módulo de modelos de datos básicos para el problema del Agente de Rescate.
"""

from typing import List, Tuple, Set

class Victima:
    """
    Representa una víctima en el mapa con su ubicación y tiempo de supervivencia límite.
    """
    def __init__(self, id_victima: str, fila: int, columna: int, ticks_supervivencia: int):
        self.id = id_victima
        self.fila = fila
        self.columna = columna
        self.ticks_supervivencia = ticks_supervivencia

    def __repr__(self) -> str:
        return f"Victima({self.id}, pos=({self.fila}, {self.columna}), ticks={self.ticks_supervivencia})"


class Mapa:
    """
    Representa la cuadrícula 2D del desastre.
    - '#' = pared
    - '.' = celda libre
    - 'S' = posición inicial del agente
    """
    def __init__(self, celdas: List[str], inicio: Tuple[int, int]):
        self.celdas = celdas
        self.filas = len(celdas)
        self.columnas = len(celdas[0]) if self.filas > 0 else 0
        self.inicio = inicio  # (fila, columna)

    def es_posicion_valida(self, fila: int, columna: int) -> bool:
        """Verifica si las coordenadas están dentro del mapa y no son una pared."""
        if 0 <= fila < self.filas and 0 <= columna < self.columnas:
            return self.celdas[fila][columna] != '#'
        return False

    def __repr__(self) -> str:
        return f"Mapa({self.filas}x{self.columnas}, inicio={self.inicio})"
