# Este archivo __init__.py convierte la carpeta "algorithms" en un paquete de Python,
# lo que permite hacer "from src.algorithms.bfs import ..." desde otros archivos.
# Además "re-exporta" las funciones principales para tenerlas en un solo lugar.

# Trae la función de BFS y la clase ResultadoBusqueda (definida dentro de bfs.py).
from src.algorithms.bfs import busqueda_amplitud, ResultadoBusqueda
# Trae la función de Costo Uniforme (UCS).
from src.algorithms.ucs import busqueda_costo_uniforme
# Trae la función de Profundidad Iterativa (IDDFS).
from src.algorithms.iddfs import busqueda_profundidad_iterativa
# Trae la función de A*.
from src.algorithms.astar import busqueda_a_estrella

# __all__ define qué nombres se exponen públicamente cuando alguien hace
# "from src.algorithms import *". Es una lista de strings con esos nombres.
__all__ = [
    # Nombre de la función de BFS
    "busqueda_amplitud",
    # Nombre de la función de UCS
    "busqueda_costo_uniforme",
    # Nombre de la función de IDDFS
    "busqueda_profundidad_iterativa",
    # Nombre de la función de A*
    "busqueda_a_estrella",
    # Nombre de la clase que guarda el resultado de cualquier búsqueda
    "ResultadoBusqueda"
]