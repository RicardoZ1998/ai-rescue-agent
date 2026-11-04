"""
Pruebas de validación para el algoritmo de Búsqueda Informada A* (Tarjeta 3.2).
Incluye la tabla comparativa oficial entre los 4 algoritmos (BFS, UCS, IDDFS, A*).
"""

from src.models import Mapa, Victima
from src.loader import cargar_mapa, cargar_victimas
from src.algorithms.bfs import busqueda_amplitud
from src.algorithms.ucs import busqueda_costo_uniforme
from src.algorithms.iddfs import busqueda_profundidad_iterativa
from src.algorithms.astar import busqueda_a_estrella

def test_astar_mapa_pequeno():
    print("--- 1. Probando A* en mapa pequeño (3x3 con 1 víctima alcanzable) ---")
    mapa = Mapa(["###", "#S.", "###"], inicio=(1, 1))
    victimas = {"V1": Victima("V1", 1, 2, 5)}

    resultado = busqueda_a_estrella(mapa, victimas)
    
    assert resultado.rescatadas == 1, "Debería haber rescatado a la víctima V1"
    assert resultado.ticks_totales == 1, "Debería haber tomado exactamente 1 tick"
    assert resultado.nodos_expandidos > 0, "Debería haber expandido nodos"
    assert resultado.tiempo_segundos > 0, "El tiempo debe ser mayor a 0"
    print(f" [OK] {resultado}")


def test_astar_mapa_proyecto():
    print("\n--- 2. Probando A* con el mapa oficial del proyecto (data/mapa.txt) ---")
    mapa = cargar_mapa("data/mapa.txt")
    victimas = cargar_victimas("data/victimas.txt", mapa)

    res_astar = busqueda_a_estrella(mapa, victimas)
    
    print("\n" + "="*50)
    print("           RESULTADO DE SIMULACIÓN (A*)")
    print("="*50)
    print(f" Víctimas totales    : {res_astar.victimas_totales}")
    print(f" Víctimas rescatadas : {res_astar.rescatadas}")
    print(f" Víctimas fallecidas : {res_astar.fallecidas}")
    print(f" Ticks totales       : {res_astar.ticks_totales}")
    print(f" Nodos expandidos    : {res_astar.nodos_expandidos}")
    print(f" Tiempo transcurrido : {res_astar.tiempo_segundos:.4f}s")
    print("="*50)

    print("\nRuta encontrada (paso a paso):")
    for paso, (accion, r, c) in enumerate(res_astar.camino):
        if paso == 0:
            print(f" Tick 0 (Inicio): Agente en ({r}, {c})")
        else:
            print(f" Tick {paso} ({accion}) -> ({r}, {c})")

    assert res_astar.rescatadas == 3, f"A* debió rescatar 3 víctimas, rescató {res_astar.rescatadas}"
    assert res_astar.ticks_totales == 14, f"A* debió encontrar la ruta óptima de 14 ticks, obtuvo {res_astar.ticks_totales}"


def test_comparacion_4_algoritmos():
    print("\n" + "="*60)
    print("        TABLA COMPARATIVA DE LOS 4 ALGORITMOS")
    print("="*60)
    mapa = cargar_mapa("data/mapa.txt")
    victimas = cargar_victimas("data/victimas.txt", mapa)

    res_bfs = busqueda_amplitud(mapa, victimas)
    res_ucs = busqueda_costo_uniforme(mapa, victimas)
    res_iddfs = busqueda_profundidad_iterativa(mapa, victimas, limite_maximo_cota=16)
    res_astar = busqueda_a_estrella(mapa, victimas)

    resultados = [res_bfs, res_ucs, res_iddfs, res_astar]

    print(f"{'Algoritmo':<10} | {'Nodos':<8} | {'Tiempo':<10} | {'Rescatadas':<10} | {'Fallecidas':<10} | {'Ticks':<6}")
    print("-" * 68)
    for r in resultados:
        print(f"{r.algoritmo:<10} | {r.nodos_expandidos:<8} | {r.tiempo_segundos:.4f}s   | {r.rescatadas:<10} | {r.fallecidas:<10} | {r.ticks_totales:<6}")
    print("=" * 68)

    # Validar que A* explore significativamente menos nodos que BFS y UCS
    assert res_astar.nodos_expandidos < res_bfs.nodos_expandidos, (
        f"A* debería expandir menos nodos ({res_astar.nodos_expandidos}) que BFS ({res_bfs.nodos_expandidos})"
    )
    print(f"\n [OK] Demostrado: A* exploró {res_astar.nodos_expandidos} nodos frente a {res_bfs.nodos_expandidos} de BFS.")


if __name__ == "__main__":
    test_astar_mapa_pequeno()
    test_astar_mapa_proyecto()
    test_comparacion_4_algoritmos()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 3.2 PASARON CON ÉXITO! <<<")

