import time
from typing import Dict, Optional, Tuple, Set
from src.modelos_de_datos import MapaDelEntorno, VictimaEnRiesgo, EstadoDelAgente
from src.evaluador_de_estados import es_estado_objetivo, es_mejor_solucion
from src.algoritmos_de_busqueda.resultado_de_busqueda import ResultadoDeLaBusqueda

def _busqueda_en_profundidad_limitada_recursiva(
    estado_actual: EstadoDelAgente,
    limite_de_profundidad: int,
    mapa_del_entorno: MapaDelEntorno,
    diccionario_de_victimas: Dict[str, VictimaEnRiesgo],
    conjunto_de_estados_en_la_rama_actual: Set[EstadoDelAgente],
    contador_acumulado_de_nodos_expandidos: list,
    mejor_estado_solucion_encontrado: list,
    cantidad_total_de_victimas: int
) -> bool:
    contador_acumulado_de_nodos_expandidos[0] += 1

    if es_estado_objetivo(estado_actual, diccionario_de_victimas):
        if es_mejor_solucion(estado_candidato=estado_actual, actual_mejor_estado=mejor_estado_solucion_encontrado[0]):
            mejor_estado_solucion_encontrado[0] = estado_actual
            if len(mejor_estado_solucion_encontrado[0].victimas_rescatadas) == cantidad_total_de_victimas:
                return True
        return False

    if estado_actual.tick_actual >= limite_de_profundidad:
        return False

    for estado_sucesor in estado_actual.generar_estados_sucesores(mapa_del_entorno, diccionario_de_victimas):
        if estado_sucesor not in conjunto_de_estados_en_la_rama_actual:
            conjunto_de_estados_en_la_rama_actual.add(estado_sucesor)
            se_encontro_la_solucion_optima_absoluta = _busqueda_en_profundidad_limitada_recursiva(
                estado_actual=estado_sucesor,
                limite_de_profundidad=limite_de_profundidad,
                mapa_del_entorno=mapa_del_entorno,
                diccionario_de_victimas=diccionario_de_victimas,
                conjunto_de_estados_en_la_rama_actual=conjunto_de_estados_en_la_rama_actual,
                contador_acumulado_de_nodos_expandidos=contador_acumulado_de_nodos_expandidos,
                mejor_estado_solucion_encontrado=mejor_estado_solucion_encontrado,
                cantidad_total_de_victimas=cantidad_total_de_victimas
            )
            conjunto_de_estados_en_la_rama_actual.remove(estado_sucesor)

            if se_encontro_la_solucion_optima_absoluta:
                return True

    return False


def ejecutar_busqueda_en_profundidad_iterativa(
    mapa_del_entorno: MapaDelEntorno,
    diccionario_de_victimas: Dict[str, VictimaEnRiesgo],
    limite_maximo_cota: int = 50
) -> ResultadoDeLaBusqueda:
    marca_de_tiempo_al_iniciar_busqueda = time.perf_counter()
    contador_acumulado_de_nodos_expandidos = [0]
    cantidad_total_de_victimas = len(diccionario_de_victimas)

    estado_inicial_del_agente = EstadoDelAgente(
        fila_actual=mapa_del_entorno.posicion_de_inicio[0],
        columna_actual=mapa_del_entorno.posicion_de_inicio[1],
        conjunto_de_victimas_vivas=frozenset(diccionario_de_victimas.keys()),
        tick_actual=0,
        conjunto_de_victimas_rescatadas=frozenset()
    )

    maximo_ticks_de_supervivencia_entre_todas_las_victimas = max((victima.ticks_supervivencia for victima in diccionario_de_victimas.values()), default=0)
    limite_maximo_de_profundidad_calculado = min(limite_maximo_cota, maximo_ticks_de_supervivencia_entre_todas_las_victimas + 5)

    mejor_estado_solucion_encontrado = [None]

    for limite in range(limite_maximo_de_profundidad_calculado + 1):
        conjunto_de_estados_en_la_rama_actual = {estado_inicial_del_agente}
        se_encontro_la_solucion_optima_absoluta = _busqueda_en_profundidad_limitada_recursiva(
            estado_actual=estado_inicial_del_agente,
            limite_de_profundidad=limite,
            mapa_del_entorno=mapa_del_entorno,
            diccionario_de_victimas=diccionario_de_victimas,
            conjunto_de_estados_en_la_rama_actual=conjunto_de_estados_en_la_rama_actual,
            contador_acumulado_de_nodos_expandidos=contador_acumulado_de_nodos_expandidos,
            mejor_estado_solucion_encontrado=mejor_estado_solucion_encontrado,
            cantidad_total_de_victimas=cantidad_total_de_victimas
        )
        if se_encontro_la_solucion_optima_absoluta:
            break

    tiempo_total_de_ejecucion = time.perf_counter() - marca_de_tiempo_al_iniciar_busqueda

    return ResultadoDeLaBusqueda(
        nombre_del_algoritmo="Profundidad Iterativa (IDDFS)",
        estado_final_alcanzado=mejor_estado_solucion_encontrado[0],
        nodos_totales_expandidos=contador_acumulado_de_nodos_expandidos[0],
        tiempo_total_en_segundos=tiempo_total_de_ejecucion,
        cantidad_total_de_victimas=cantidad_total_de_victimas
    )

