from typing import List, Tuple, Set

class VictimaEnRiesgo:
    def __init__(self, identificador_de_la_victima: str, fila: int, columna: int, ticks_supervivencia: int):
        self.identificador = identificador_de_la_victima
        self.fila = fila
        self.columna = columna
        self.ticks_supervivencia = ticks_supervivencia

    def __repr__(self) -> str:
        return f"VictimaEnRiesgo({self.identificador}, posicion=({self.fila}, {self.columna}), ticks_limite={self.ticks_supervivencia})"


class MapaDelEntorno:
    def __init__(self, celdas_del_mapa: List[str], posicion_de_inicio: Tuple[int, int]):
        self.celdas = celdas_del_mapa
        self.filas = len(celdas_del_mapa)
        self.columnas = len(celdas_del_mapa[0]) if self.filas > 0 else 0
        self.posicion_de_inicio = posicion_de_inicio

    def es_posicion_valida(self, fila_a_verificar: int, columna_a_verificar: int) -> bool:
        if 0 <= fila_a_verificar < self.filas and 0 <= columna_a_verificar < self.columnas:
            return self.celdas[fila_a_verificar][columna_a_verificar] != '#'
        return False

    def __repr__(self) -> str:
        return f"MapaDelEntorno({self.filas}x{self.columnas}, inicio={self.posicion_de_inicio})"


class EstadoDelAgente:
    def __init__(
        self,
        fila_actual: int,
        columna_actual: int,
        conjunto_de_victimas_vivas: frozenset,
        tick_actual: int = 0,
        conjunto_de_victimas_rescatadas: frozenset = frozenset(),
        estado_padre: "EstadoDelAgente" = None,
        accion_origen: str = None
    ):
        self.fila = fila_actual
        self.columna = columna_actual
        self.victimas_vivas = conjunto_de_victimas_vivas
        self.tick_actual = tick_actual
        self.victimas_rescatadas = conjunto_de_victimas_rescatadas
        self.estado_padre = estado_padre
        self.accion_origen = accion_origen

    def __hash__(self) -> int:
        return hash((self.fila, self.columna, self.victimas_vivas, self.victimas_rescatadas, self.tick_actual))

    def __eq__(self, otro_objeto: object) -> bool:
        if not isinstance(otro_objeto, EstadoDelAgente):
            return False
        return (
            self.fila == otro_objeto.fila and
            self.columna == otro_objeto.columna and
            self.victimas_vivas == otro_objeto.victimas_vivas and
            self.victimas_rescatadas == otro_objeto.victimas_rescatadas and
            self.tick_actual == otro_objeto.tick_actual
        )

    def generar_estados_sucesores(self, mapa_del_entorno: MapaDelEntorno, diccionario_de_victimas: dict) -> List["EstadoDelAgente"]:
        lista_de_estados_sucesores = []
        direcciones_cardinales_posibles = [
            ('Norte', -1, 0),
            ('Sur', 1, 0),
            ('Este', 0, 1),
            ('Oeste', 0, -1)
        ]

        tick_despues_del_movimiento = self.tick_actual + 1

        for nombre_de_accion, desplazamiento_en_filas, desplazamiento_en_columnas in direcciones_cardinales_posibles:
            fila_destino = self.fila + desplazamiento_en_filas
            columna_destino = self.columna + desplazamiento_en_columnas

            if not mapa_del_entorno.es_posicion_valida(fila_destino, columna_destino):
                continue

            conjunto_de_victimas_rescatadas_actualizado = set(self.victimas_rescatadas)
            conjunto_de_victimas_que_siguen_vivas = set()

            for identificador_victima_actual in self.victimas_vivas:
                victima_evaluada = diccionario_de_victimas[identificador_victima_actual]
                
                if victima_evaluada.fila == fila_destino and victima_evaluada.columna == columna_destino:
                    if tick_despues_del_movimiento <= victima_evaluada.ticks_supervivencia:
                        conjunto_de_victimas_rescatadas_actualizado.add(identificador_victima_actual)
                else:
                    if tick_despues_del_movimiento <= victima_evaluada.ticks_supervivencia:
                        conjunto_de_victimas_que_siguen_vivas.add(identificador_victima_actual)

            estado_sucesor_generado = EstadoDelAgente(
                fila_actual=fila_destino,
                columna_actual=columna_destino,
                conjunto_de_victimas_vivas=frozenset(conjunto_de_victimas_que_siguen_vivas),
                tick_actual=tick_despues_del_movimiento,
                conjunto_de_victimas_rescatadas=frozenset(conjunto_de_victimas_rescatadas_actualizado),
                estado_padre=self,
                accion_origen=nombre_de_accion
            )
            lista_de_estados_sucesores.append(estado_sucesor_generado)

        return lista_de_estados_sucesores

    def reconstruir_camino_completo(self) -> List[Tuple[str, int, int]]:
        secuencia_de_pasos_reconstruida = []
        estado_en_recorrido = self
        while estado_en_recorrido is not None:
            secuencia_de_pasos_reconstruida.append((estado_en_recorrido.accion_origen, estado_en_recorrido.fila, estado_en_recorrido.columna))
            estado_en_recorrido = estado_en_recorrido.estado_padre
        secuencia_de_pasos_reconstruida.reverse()
        return secuencia_de_pasos_reconstruida

    def __repr__(self) -> str:
        return (
            f"EstadoDelAgente(posicion=({self.fila}, {self.columna}), "
            f"tick={self.tick_actual}, "
            f"victimas_vivas={set(self.victimas_vivas)}, "
            f"victimas_rescatadas={set(self.victimas_rescatadas)})"
        )

