import time
import heapq
from typing import Dict, Optional
from src.modelos_de_datos import MapaDelEntorno, VictimaEnRiesgo, EstadoDelAgente
from src.evaluador_de_estados import es_estado_objetivo, es_mejor_solucion
from src.funciones_heuristicas import calcular_heuristica_para_busqueda_a_estrella
from src.algoritmos_de_busqueda.resultado_de_busqueda import ResultadoDeLaBusqueda

def ejecutar_busqueda_a_estrella(mapa_del_entorno: MapaDelEntorno, diccionario_de_victimas: Dict[str, VictimaEnRiesgo]) -> ResultadoDeLaBusqueda:
    marca_de_tiempo_al_iniciar_busqueda = time.perf_counter()
    contador_de_nodos_expandidos = 0
    cantidad_total_de_victimas = len(diccionario_de_victimas)
    contador_secuencial_para_desempate = 0

    estado_inicial_del_agente = EstadoDelAgente(
        fila_actual=mapa_del_entorno.posicion_de_inicio[0],
        columna_actual=mapa_del_entorno.posicion_de_inicio[1],
        conjunto_de_victimas_vivas=frozenset(diccionario_de_victimas.keys()),
        tick_actual=0,
        conjunto_de_victimas_rescatadas=frozenset()
    )

    perdidas_estimadas_por_heuristica, distancia_minima_heuristica = calcular_heuristica_para_busqueda_a_estrella(estado_inicial_del_agente, diccionario_de_victimas)
    
    cola_de_prioridad_de_estados = []
    heapq.heappush(cola_de_prioridad_de_estados, (perdidas_estimadas_por_heuristica, distancia_minima_heuristica, 0, contador_secuencial_para_desempate, estado_inicial_del_agente))

    mejor_costo_conocido_por_estado = {estado_inicial_del_agente: 0}
    mejor_estado_solucion_encontrado: Optional[EstadoDelAgente] = None

    while cola_de_prioridad_de_estados:
        perdidas_estimadas_del_estado, distancia_minima_del_estado, costo_acumulado_del_estado, _, estado_siendo_evaluado = heapq.heappop(cola_de_prioridad_de_estados)
        contador_de_nodos_expandidos += 1

        if mejor_estado_solucion_encontrado is not None:
            perdidas_de_la_mejor_solucion_actual = cantidad_total_de_victimas - len(mejor_estado_solucion_encontrado.victimas_rescatadas)
            if perdidas_estimadas_del_estado > perdidas_de_la_mejor_solucion_actual:
                continue
            if perdidas_estimadas_del_estado == perdidas_de_la_mejor_solucion_actual and costo_acumulado_del_estado >= mejor_estado_solucion_encontrado.tick_actual:
                continue

        if costo_acumulado_del_estado > mejor_costo_conocido_por_estado.get(estado_siendo_evaluado, float('inf')):
            continue

        if es_estado_objetivo(estado_siendo_evaluado, diccionario_de_victimas):
            if es_mejor_solucion(estado_candidato=estado_siendo_evaluado, actual_mejor_estado=mejor_estado_solucion_encontrado):
                mejor_estado_solucion_encontrado = estado_siendo_evaluado
                if len(mejor_estado_solucion_encontrado.victimas_rescatadas) == cantidad_total_de_victimas:
                    break
            continue

        for estado_sucesor in estado_siendo_evaluado.generar_estados_sucesores(mapa_del_entorno, diccionario_de_victimas):
            costo_del_estado_sucesor = estado_sucesor.tick_actual
            perdidas_estimadas_del_sucesor, distancia_minima_del_sucesor = calcular_heuristica_para_busqueda_a_estrella(estado_sucesor, diccionario_de_victimas)

            if mejor_estado_solucion_encontrado is not None:
                perdidas_de_la_mejor_solucion_actual = cantidad_total_de_victimas - len(mejor_estado_solucion_encontrado.victimas_rescatadas)
                if perdidas_estimadas_del_sucesor > perdidas_de_la_mejor_solucion_actual:
                    continue
                if perdidas_estimadas_del_sucesor == perdidas_de_la_mejor_solucion_actual and costo_del_estado_sucesor >= mejor_estado_solucion_encontrado.tick_actual:
                    continue

            if costo_del_estado_sucesor < mejor_costo_conocido_por_estado.get(estado_sucesor, float('inf')):
                mejor_costo_conocido_por_estado[estado_sucesor] = costo_del_estado_sucesor
                contador_secuencial_para_desempate += 1
                heapq.heappush(
                    cola_de_prioridad_de_estados,
                    (perdidas_estimadas_del_sucesor, distancia_minima_del_sucesor, costo_del_estado_sucesor, contador_secuencial_para_desempate, estado_sucesor)
                )

    tiempo_total_de_ejecucion = time.perf_counter() - marca_de_tiempo_al_iniciar_busqueda

    return ResultadoDeLaBusqueda(
        nombre_del_algoritmo="A* (Búsqueda Informada)",
        estado_final_alcanzado=mejor_estado_solucion_encontrado,
        nodos_totales_expandidos=contador_de_nodos_expandidos,
        tiempo_total_en_segundos=tiempo_total_de_ejecucion,
        cantidad_total_de_victimas=cantidad_total_de_victimas
    )

