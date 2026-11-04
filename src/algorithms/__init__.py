from src.algorithms.bfs import busqueda_amplitud, ResultadoBusqueda
from src.algorithms.ucs import busqueda_costo_uniforme
from src.algorithms.iddfs import busqueda_profundidad_iterativa
from src.algorithms.astar import busqueda_a_estrella

__all__ = [
    "busqueda_amplitud",
    "busqueda_costo_uniforme",
    "busqueda_profundidad_iterativa",
    "busqueda_a_estrella",
    "ResultadoBusqueda"
]
