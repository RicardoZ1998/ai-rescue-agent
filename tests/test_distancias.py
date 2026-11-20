"""
Pruebas de las distancias reales (BFS), la clave de dominancia y la corrección de las podas.
"""

from src.models import Mapa, Victima, Estado
from src.loader import cargar_mapa, cargar_victimas
from src.distancias import calcular_tabla_distancias
from src.evaluator import distancia_manhattan
from src.heuristics import heuristica_a_estrella
from src.algorithms import (
    busqueda_amplitud, busqueda_costo_uniforme,
    busqueda_profundidad_iterativa, busqueda_a_estrella,
)


def test_distancia_real_respeta_paredes():
    # La víctima está a 2 celdas en línea recta, pero hay una pared en medio: real = 6
    mapa = Mapa(["#####", "#S#V#", "#.#.#", "#...#", "#####"], inicio=(1, 1))
    victimas = {"V1": Victima("V1", 1, 3, 10)}
    tabla = calcular_tabla_distancias(mapa, victimas)
    assert distancia_manhattan((1, 1), (1, 3)) == 2
    assert tabla["V1"][(1, 1)] == 6


def test_victima_encerrada_es_inalcanzable():
    mapa = Mapa(["#####", "#S#V#", "#####"], inicio=(1, 1))
    victimas = {"V1": Victima("V1", 1, 3, 10)}
    tabla = calcular_tabla_distancias(mapa, victimas)
    assert (1, 1) not in tabla["V1"]
    # Con Manhattan parecería alcanzable (2 <= 10); con la tabla real, condenada
    inicial = Estado(1, 1, frozenset(["V1"]), 0)
    assert heuristica_a_estrella(inicial, victimas)[0] == 0
    assert heuristica_a_estrella(inicial, victimas, tabla)[0] == 1


def test_heuristica_real_es_admisible_y_domina_a_manhattan():
    # h_real >= h_manhattan en cualquier estado, y h_real <= muertes reales finales
    mapa = cargar_mapa("data/mapa.txt")
    victimas = cargar_victimas("data/victimas.txt", mapa)
    tabla = calcular_tabla_distancias(mapa, victimas)
    optimo = busqueda_a_estrella(mapa, victimas)
    # Recorremos el camino óptimo: h(n) nunca debe superar las muertes finales
    estado = optimo.estado_final
    while estado is not None:
        h_real = heuristica_a_estrella(estado, victimas, tabla)[0]
        h_manh = heuristica_a_estrella(estado, victimas)[0]
        assert h_manh <= h_real <= optimo.fallecidas
        estado = estado.padre


def test_clave_ignora_el_tick():
    a = Estado(1, 1, frozenset(["V1"]), 3)
    b = Estado(1, 1, frozenset(["V1"]), 7)
    assert a.clave() == b.clave()
    assert a != b  # pero el Estado completo sí distingue el tick


def test_iddfs_sin_tope_es_optimo_con_victima_lejana():
    # Pasillo largo: la víctima solo se alcanza en el tick 24. Un tope de 16 la perdería.
    mapa = Mapa(["#" * 27, "#S" + "." * 24 + "#", "#" * 27], inicio=(1, 1))
    victimas = {"V1": Victima("V1", 1, 25, 24)}
    assert busqueda_profundidad_iterativa(mapa, victimas).rescatadas == 1
    assert busqueda_profundidad_iterativa(mapa, victimas, limite_maximo_cota=16).rescatadas == 0


def test_los_4_algoritmos_coinciden_en_mapa_proyecto():
    mapa = cargar_mapa("data/mapa.txt")
    victimas = cargar_victimas("data/victimas.txt", mapa)
    res = [f(mapa, victimas) for f in (busqueda_amplitud, busqueda_costo_uniforme,
                                      busqueda_profundidad_iterativa, busqueda_a_estrella)]
    assert len({(r.rescatadas, r.ticks_totales) for r in res}) == 1
    assert res[2].nodos_expandidos < 100000, "IDDFS ya no debe explotar en nodos"