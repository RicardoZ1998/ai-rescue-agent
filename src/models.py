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


class Estado:
    """
    Definición formal del estado del agente de rescate.
    Estado: (fila, columna, conjunto_de_victimas_vivas, tick_actual)

    Atributos:
    - fila, columna: posición actual del agente en la cuadrícula.
    - victimas_vivas: frozenset con los IDs de las víctimas que no han muerto ni han sido rescatadas.
    - tick_actual: número de movimientos realizados hasta este estado.
    - victimas_rescatadas: frozenset con los IDs de las víctimas rescatadas con éxito.
    - padre: referencia al estado anterior (para reconstruir la ruta de rescate).
    - accion: acción tomada para llegar a este estado ('N', 'S', 'E', 'O').
    """
    def __init__(
        self,
        fila: int,
        columna: int,
        victimas_vivas: frozenset,
        tick_actual: int = 0,
        victimas_rescatadas: frozenset = frozenset(),
        padre: "Estado" = None,
        accion: str = None
    ):
        self.fila = fila
        self.columna = columna
        self.victimas_vivas = victimas_vivas
        self.tick_actual = tick_actual
        self.victimas_rescatadas = victimas_rescatadas
        self.padre = padre
        self.accion = accion

    def __hash__(self) -> int:
        """
        Permite usar el Estado en sets (conjuntos de visitados) y como llaves de diccionarios.
        El hash incluye la posición, las víctimas vivas, las rescatadas y el tick.
        """
        return hash((self.fila, self.columna, self.victimas_vivas, self.victimas_rescatadas, self.tick_actual))

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Estado):
            return False
        return (
            self.fila == otro.fila and
            self.columna == otro.columna and
            self.victimas_vivas == otro.victimas_vivas and
            self.victimas_rescatadas == otro.victimas_rescatadas and
            self.tick_actual == otro.tick_actual
        )

    def generar_sucesores(self, mapa: Mapa, dict_victimas: dict) -> List["Estado"]:
        """
        Genera los estados sucesores válidos aplicando las 4 acciones cardinales:
        Norte (-1, 0), Sur (1, 0), Este (0, 1), Oeste (0, -1).

        Reglas:
        1. El agente no puede moverse a celdas con pared '#'.
        2. Cada movimiento incrementa el tick en 1 (costo = 1 tick).
        3. Si la nueva posición coincide con una víctima viva y tick_nuevo <= tick_supervivencia, es rescatada.
        4. Cualquier víctima viva cuyo tiempo expire (tick_nuevo > tick_supervivencia) muere en este turno.
        """
        sucesores = []
        movimientos = [
            ('N', -1, 0),
            ('S', 1, 0),
            ('E', 0, 1),
            ('O', 0, -1)
        ]

        nuevo_tick = self.tick_actual + 1

        for accion, df, dc in movimientos:
            nueva_fila = self.fila + df
            nueva_col = self.columna + dc

            if not mapa.es_posicion_valida(nueva_fila, nueva_col):
                continue

            nuevas_rescatadas = set(self.victimas_rescatadas)
            nuevas_vivas = set()

            for id_v in self.victimas_vivas:
                v = dict_victimas[id_v]
                
                if v.fila == nueva_fila and v.columna == nueva_col:
                    if nuevo_tick <= v.ticks_supervivencia:
                        nuevas_rescatadas.add(id_v)
                else:
                    if nuevo_tick <= v.ticks_supervivencia:
                        nuevas_vivas.add(id_v)

            nuevo_estado = Estado(
                fila=nueva_fila,
                columna=nueva_col,
                victimas_vivas=frozenset(nuevas_vivas),
                tick_actual=nuevo_tick,
                victimas_rescatadas=frozenset(nuevas_rescatadas),
                padre=self,
                accion=accion
            )
            sucesores.append(nuevo_estado)

        return sucesores

    def reconstruir_camino(self) -> List[Tuple[str, int, int]]:
        """
        Reconstruye la secuencia de pasos desde el estado inicial hasta este estado.
        Retorna una lista de tuplas: (accion, fila, columna).
        """
        camino = []
        actual = self
        while actual is not None:
            camino.append((actual.accion, actual.fila, actual.columna))
            actual = actual.padre
        camino.reverse()
        return camino

    def __repr__(self) -> str:
        return (
            f"Estado(pos=({self.fila}, {self.columna}), "
            f"tick={self.tick_actual}, "
            f"vivas={set(self.victimas_vivas)}, "
            f"rescatadas={set(self.victimas_rescatadas)})"
        )
