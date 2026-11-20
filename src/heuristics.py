"""
Módulo de funciones heurísticas para el algoritmo A* (Tarjeta 3.1).
Demostración de admisibilidad incluida en la documentación de cada función.
"""

# Tipos para anotaciones (Dict del diccionario de víctimas, Tuple para el retorno compuesto).
from typing import Dict, Tuple
# Clases propias usadas en las anotaciones.
from src.models import Estado, Victima
# Función de distancia Manhattan, reutilizada desde evaluator.py.
from src.evaluator import distancia_manhattan


# Heurística base del enunciado: cuenta cuántas víctimas vivas ya están perdidas.
def heuristica_victimas_condenadas(estado: Estado, dict_victimas: Dict[str, Victima]) -> int:
    """
    Heurística Admisible Base propuesta en el enunciado del proyecto:
    h(n) = número de víctimas vivas que ya están matemáticamente condenadas a morir.

    Demostración de Admisibilidad:
    - Una víctima v está condenada si distancia_Manhattan(agente, v) > ticks_restantes(v).
    - Dado que distancia_Manhattan es la distancia mínima en línea recta sin obstáculos,
      cualquier ruta real con paredes tendrá distancia_real >= distancia_Manhattan.
    - Por tanto, si distancia_Manhattan > ticks_restantes, entonces distancia_real > ticks_restantes,
      lo que significa que la víctima morirá con 100% de certeza.
    - Como nunca cuenta muertes que no ocurrirán, h(n) <= h*(n) en todos los estados.
    - Por definición, h(n) es ADMISIBLE.
    """
    # Posición actual del agente como tupla (fila, columna).
    pos_agente = (estado.fila, estado.columna)
    # Contador de víctimas condenadas; empieza en 0.
    condenadas = 0

    # Revisa cada víctima que sigue viva en este estado.
    for id_v in estado.victimas_vivas:
        # Obtiene el objeto Victima a partir de su id.
        v = dict_victimas[id_v]
        # Ticks que le quedan de vida a esa víctima desde el tick actual.
        ticks_restantes = v.ticks_supervivencia - estado.tick_actual

        # Si ya es negativo, su tiempo se agotó: cuenta como condenada.
        if ticks_restantes < 0:
            # Suma una condenada.
            condenadas += 1
            # Pasa a la siguiente víctima (no calcula distancia).
            continue

        # Distancia mínima teórica del agente a esa víctima.
        distancia = distancia_manhattan(pos_agente, (v.fila, v.columna))
        # Si la distancia supera lo que le queda de vida, no llegará a tiempo: condenada.
        if distancia > ticks_restantes:
            # Suma una condenada.
            condenadas += 1

    # Devuelve el total de víctimas vivas ya condenadas.
    return condenadas


# Heurística que realmente usa A*: devuelve una pareja (pérdidas estimadas, distancia mínima).
def heuristica_a_estrella(estado: Estado, dict_victimas: Dict[str, Victima]) -> Tuple[int, int]:
    """
    Heurística compuesta para guiar eficientemente la cola de prioridad en A*.
    Retorna una tupla de dos valores:
    1. victimas_perdidas_estimadas:
       (víctimas ya fallecidas) + (víctimas actualmente condenadas por distancia Manhattan).
    2. distancia_minima_alcanzable:
       Distancia Manhattan hacia la víctima alcanzable más cercana (para romper empates
       y atraer al agente hacia el siguiente rescate con el menor rodeo posible).
    """
    # Posición actual del agente.
    pos_agente = (estado.fila, estado.columna)
    # Total de víctimas del problema (vivas + rescatadas + fallecidas).
    victimas_totales = len(dict_victimas)
    
    # Contador de víctimas vivas ya condenadas.
    condenadas = 0
    # Distancia a la víctima alcanzable más cercana; 0 por defecto si no hay ninguna alcanzable.
    distancia_minima = 0
    # Lista donde se guardan las distancias de las víctimas aún alcanzables.
    distancias_alcanzables = []

    # Revisa cada víctima viva.
    for id_v in estado.victimas_vivas:
        # Obtiene el objeto Victima.
        v = dict_victimas[id_v]
        # Ticks restantes de esa víctima.
        ticks_restantes = v.ticks_supervivencia - estado.tick_actual

        # Si su tiempo ya se agotó, cuenta como condenada.
        if ticks_restantes < 0:
            # Suma una condenada.
            condenadas += 1
            # Siguiente víctima.
            continue

        # Distancia Manhattan del agente a esta víctima.
        dist = distancia_manhattan(pos_agente, (v.fila, v.columna))
        # Si no alcanza a llegar, está condenada.
        if dist > ticks_restantes:
            # Suma una condenada.
            condenadas += 1
        # Si sí alcanza (en teoría), se guarda su distancia como candidata a "la más cercana".
        else:
            # Agrega la distancia a la lista de alcanzables.
            distancias_alcanzables.append(dist)

    # Si hubo al menos una víctima alcanzable...
    if distancias_alcanzables:
        # ...la distancia mínima es la menor de la lista.
        distancia_minima = min(distancias_alcanzables)

    # Víctimas que ya murieron antes de este estado
    # Fallecidas = totales - rescatadas - vivas (las que no están en ningún conjunto ya murieron).
    ya_fallecidas = victimas_totales - len(estado.victimas_rescatadas) - len(estado.victimas_vivas)
    # Pérdidas estimadas = las que ya murieron + las vivas que están condenadas.
    total_perdidas = ya_fallecidas + condenadas

    # Devuelve la pareja (pérdidas estimadas, distancia a la víctima alcanzable más cercana).
    return total_perdidas, distancia_minima