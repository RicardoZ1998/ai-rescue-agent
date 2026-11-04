from typing import Optional, List, Tuple
from src.modelos_de_datos import EstadoDelAgente

class ResultadoDeLaBusqueda:
    def __init__(
        self,
        nombre_del_algoritmo: str,
        estado_final_alcanzado: Optional[EstadoDelAgente],
        nodos_totales_expandidos: int,
        tiempo_total_en_segundos: float,
        cantidad_total_de_victimas: int
    ):
        self.algoritmo = nombre_del_algoritmo
        self.estado_final = estado_final_alcanzado
        self.nodos_expandidos = nodos_totales_expandidos
        self.tiempo_segundos = tiempo_total_en_segundos
        self.victimas_totales = cantidad_total_de_victimas

        if estado_final_alcanzado is not None:
            self.rescatadas = len(estado_final_alcanzado.victimas_rescatadas)
            self.fallecidas = cantidad_total_de_victimas - self.rescatadas
            self.ticks_totales = estado_final_alcanzado.tick_actual
            self.camino = estado_final_alcanzado.reconstruir_camino_completo()
        else:
            self.rescatadas = 0
            self.fallecidas = cantidad_total_de_victimas
            self.ticks_totales = 0
            self.camino = []

    def __repr__(self) -> str:
        return (
            f"[{self.algoritmo}] Nodos: {self.nodos_expandidos} | "
            f"Tiempo: {self.tiempo_segundos:.4f}s | "
            f"Rescatadas: {self.rescatadas}/{self.victimas_totales} | "
            f"Fallecidas: {self.fallecidas} | "
            f"Ticks: {self.ticks_totales}"
        )

