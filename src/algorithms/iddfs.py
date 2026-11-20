"""
Implementación del algoritmo de Búsqueda en Profundidad Iterativa (IDDFS) desde cero.
Sin librerías externas.
"""

# Módulo para medir tiempo.
import time
# Tipos para anotaciones.
from typing import Dict, Optional, Tuple, Set
# Clases propias del problema.
from src.models import Mapa, Victima, Estado
# Funciones de evaluación: criterio de parada y comparador de soluciones.
from src.evaluator import es_estado_objetivo, es_mejor_solucion
# Reutiliza la clase de resultado definida en bfs.py.
from src.algorithms.bfs import ResultadoBusqueda


# Búsqueda en profundidad limitada (DLS) recursiva: la pieza que IDDFS repite con límites crecientes.
def _dls_recursivo(
    # Estado que se está visitando en esta llamada.
    estado: Estado,
    # Profundidad máxima permitida en esta iteración (medida en ticks).
    limite: int,
    # Mapa del problema.
    mapa: Mapa,
    # Diccionario de víctimas.
    dict_victimas: Dict[str, Victima],
    # Conjunto de estados de la rama actual (la ruta desde la raíz hasta aquí).
    ruta_actual: Set[Estado],
    # Lista de 1 elemento que cuenta nodos (lista = mutable, se actualiza "por referencia").
    contador_nodos: list,
    # Lista de 1 elemento con la mejor solución (también "por referencia").
    mejor_solucion: list,
    # Total de víctimas, para detectar el rescate completo.
    victimas_totales: int
) -> bool:
    """
    Depth-Limited Search (DLS) recursivo.
    - ruta_actual: conjunto de estados en la rama activa para evitar ciclos locales.
    - contador_nodos: lista con un entero mutable para contar expansiones acumuladas.
    - mejor_solucion: lista de 1 elemento [mejor_estado] para actualizar por referencia.
    Retorna True si encontró la solución óptima absoluta (todas las víctimas rescatadas).
    """
    # Cuenta este nodo visitado/expandido en el contador compartido.
    contador_nodos[0] += 1

    # Evaluar si el estado es objetivo (no quedan víctimas alcanzables)
    if es_estado_objetivo(estado, dict_victimas):
        # Si mejora la mejor solución guardada...
        if es_mejor_solucion(candidato=estado, actual_mejor=mejor_solucion[0]):
            # ...la actualiza.
            mejor_solucion[0] = estado
            # Si con esto ya rescató a TODAS las víctimas...
            if len(mejor_solucion[0].victimas_rescatadas) == victimas_totales:
                # ...avisa hacia arriba que se encontró el óptimo absoluto.
                return True  # Parada temprana: todas las víctimas rescatadas
        # Estado terminal: no se baja más; devuelve False (aún no es el óptimo absoluto).
        return False

    # Si alcanzamos el límite de profundidad para esta iteración, no descendemos más
    # Como cada paso cuesta 1 tick, la profundidad equivale a tick_actual.
    if estado.tick_actual >= limite:
        return False

    # Explorar sucesores en profundidad (DFS)
    # Recorre cada estado hijo.
    for sucesor in estado.generar_sucesores(mapa, dict_victimas):
        # Solo baja si el sucesor no está ya en la rama actual (evita ciclos en el camino).
        if sucesor not in ruta_actual:
            # Marca el sucesor como parte de la rama activa.
            ruta_actual.add(sucesor)
            # Llamada recursiva: explora en profundidad a partir del sucesor.
            encontro_optimo = _dls_recursivo(
                # Se visita el sucesor.
                estado=sucesor,
                # Mismo límite.
                limite=limite,
                # Mismo mapa.
                mapa=mapa,
                # Mismas víctimas.
                dict_victimas=dict_victimas,
                # Misma ruta activa (se comparte y se modifica).
                ruta_actual=ruta_actual,
                # Mismo contador compartido.
                contador_nodos=contador_nodos,
                # Misma mejor solución compartida.
                mejor_solucion=mejor_solucion,
                # Mismo total de víctimas.
                victimas_totales=victimas_totales
            )
            # Al volver de la recursión, quita el sucesor de la rama activa para poder explorar otras ramas.
            ruta_actual.remove(sucesor)  # Backtracking

            # Si en esa rama se halló el óptimo absoluto, corta todo y propaga True hacia arriba.
            if encontro_optimo:
                return True

    # Terminó de explorar los hijos sin hallar el óptimo absoluto.
    return False


# Función principal de IDDFS.
def busqueda_profundidad_iterativa(
    # Mapa del problema.
    mapa: Mapa,
    # Diccionario de víctimas.
    dict_victimas: Dict[str, Victima],
    # Límite máximo permitido de profundidad (por defecto 50; la GUI y los tests de comparación usan 16).
    limite_maximo_cota: int = 50
) -> ResultadoBusqueda:
    """
    Ejecuta el algoritmo de Búsqueda en Profundidad Iterativa (IDDFS).
    
    1. Itera incrementando el límite de profundidad L desde 0 hasta la cota máxima.
    2. En cada iteración ejecuta DLS (Depth-Limited Search).
    3. Acumula los nodos expandidos totales entre todas las iteraciones.
    4. Garantiza encontrar la ruta con menor número de ticks para el mejor rescate.
    """
    # Marca el instante de inicio.
    tiempo_inicio = time.perf_counter()
    # Contador de nodos como lista de 1 elemento para que la función recursiva pueda modificarlo.
    nodos_expandidos = [0]
    # Total de víctimas del problema.
    victimas_totales = len(dict_victimas)

    # Estado inicial: agente en 'S', todas vivas, tick 0, ninguna rescatada.
    estado_inicial = Estado(
        # Fila de 'S'.
        fila=mapa.inicio[0],
        # Columna de 'S'.
        columna=mapa.inicio[1],
        # Todas las víctimas vivas.
        victimas_vivas=frozenset(dict_victimas.keys()),
        # Tick 0.
        tick_actual=0,
        # Ninguna rescatada.
        victimas_rescatadas=frozenset()
    )

    # Determinar la cota máxima de ticks razonable basada en las víctimas
    # Ninguna víctima vive más allá del máximo ticks_supervivencia
    # Busca el mayor tiempo de supervivencia entre todas las víctimas (0 si no hay víctimas).
    max_tick_victimas = max((v.ticks_supervivencia for v in dict_victimas.values()), default=0)
    # La profundidad máxima real es la menor entre la cota pedida y (ese máximo + 5 de margen).
    cota_profundidad = min(limite_maximo_cota, max_tick_victimas + 5)

    # Lista de 1 elemento que guardará la mejor solución (empieza sin solución).
    mejor_solucion = [None]

    # Profundización iterativa: prueba límites 0, 1, 2, ..., cota_profundidad.
    for limite in range(cota_profundidad + 1):
        # En cada iteración la ruta activa empieza solo con el estado inicial.
        ruta_actual = {estado_inicial}
        # Ejecuta la búsqueda en profundidad limitada con el límite actual.
        terminar_absoluto = _dls_recursivo(
            # Empieza desde la raíz.
            estado=estado_inicial,
            # Límite de esta iteración.
            limite=limite,
            # Mapa.
            mapa=mapa,
            # Víctimas.
            dict_victimas=dict_victimas,
            # Ruta activa.
            ruta_actual=ruta_actual,
            # Contador acumulado entre todas las iteraciones.
            contador_nodos=nodos_expandidos,
            # Mejor solución compartida entre iteraciones.
            mejor_solucion=mejor_solucion,
            # Total de víctimas.
            victimas_totales=victimas_totales
        )
        # Si ya se rescató a todas las víctimas, no hace falta seguir aumentando el límite.
        if terminar_absoluto:
            break

    # Tiempo total transcurrido.
    tiempo_total = time.perf_counter() - tiempo_inicio

    # Empaqueta y devuelve el resultado.
    return ResultadoBusqueda(
        # Nombre para la tabla.
        algoritmo="IDDFS",
        # Mejor estado hallado (primer y único elemento de la lista).
        estado_final=mejor_solucion[0],
        # Nodos acumulados (se saca el entero de la lista).
        nodos_expandidos=nodos_expandidos[0],
        # Tiempo en segundos.
        tiempo_segundos=tiempo_total,
        # Total de víctimas.
        victimas_totales=victimas_totales
    )