import time
from collections import deque
from typing import Dict, Optional
from src.modelos_de_datos import MapaDelEntorno, VictimaEnRiesgo, EstadoDelAgente
from src.evaluador_de_estados import es_estado_objetivo, es_mejor_solucion
from src.algoritmos_de_busqueda.resultado_de_busqueda import ResultadoDeLaBusqueda

def ejecutar_busqueda_en_amplitud(mapa_del_entorno: MapaDelEntorno, diccionario_de_victimas: Dict[str, VictimaEnRiesgo]) -> ResultadoDeLaBusqueda:
    marca_de_tiempo_al_iniciar_busqueda = time.perf_counter()
    contador_de_nodos_expandidos = 0
    cantidad_total_de_victimas = len(diccionario_de_victimas)

    estado_inicial_del_agente = EstadoDelAgente(
        fila_actual=mapa_del_entorno.posicion_de_inicio[0],
        columna_actual=mapa_del_entorno.posicion_de_inicio[1],
        conjunto_de_victimas_vivas=frozenset(diccionario_de_victimas.keys()),
        tick_actual=0,
        conjunto_de_victimas_rescatadas=frozenset()
    )

    cola_fifo_de_estados_por_explorar = deque([estado_inicial_del_agente])
    conjunto_de_estados_ya_visitados = set([estado_inicial_del_agente])
    mejor_estado_solucion_encontrado: Optional[EstadoDelAgente] = None

    while cola_fifo_de_estados_por_explorar:
        estado_siendo_evaluado = cola_fifo_de_estados_por_explorar.popleft()
        contador_de_nodos_expandidos += 1

        if es_estado_objetivo(estado_siendo_evaluado, diccionario_de_victimas):
            if es_mejor_solucion(estado_candidato=estado_siendo_evaluado, actual_mejor_estado=mejor_estado_solucion_encontrado):
                mejor_estado_solucion_encontrado = estado_siendo_evaluado
                if len(mejor_estado_solucion_encontrado.victimas_rescatadas) == cantidad_total_de_victimas:
                    break
            continue

        for estado_sucesor in estado_siendo_evaluado.generar_estados_sucesores(mapa_del_entorno, diccionario_de_victimas):
            if estado_sucesor not in conjunto_de_estados_ya_visitados:
                conjunto_de_estados_ya_visitados.add(estado_sucesor)
                cola_fifo_de_estados_por_explorar.append(estado_sucesor)

    tiempo_total_de_ejecucion = time.perf_counter() - marca_de_tiempo_al_iniciar_busqueda

    return ResultadoDeLaBusqueda(
        nombre_del_algoritmo="Búsqueda en Amplitud (BFS)",
        estado_final_alcanzado=mejor_estado_solucion_encontrado,
        nodos_totales_expandidos=contador_de_nodos_expandidos,
        tiempo_total_en_segundos=tiempo_total_de_ejecucion,
        cantidad_total_de_victimas=cantidad_total_de_victimas
    )

