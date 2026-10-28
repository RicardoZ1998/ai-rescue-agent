"""
Pruebas de validación para el algoritmo de Búsqueda en Amplitud - BFS (Tarjeta 2.1).
"""

from src.models import Mapa, Victima, Estado
from src.loader import cargar_mapa, cargar_victimas
from src.algorithms.bfs import busqueda_amplitud

def test_bfs_mapa_pequeno():
    print("--- 1. Probando BFS en mapa pequeño (3x3 con 1 víctima alcanzable) ---")
    # Mapa:
    # ###
    # #S.
    # ###
    # Víctima en (1, 2) con 5 ticks de vida (distancia 1)
    mapa = Mapa(["###", "#S.", "###"], inicio=(1, 1))
    victimas = {"V1": Victima("V1", 1, 2, 5)}

    resultado = busqueda_amplitud(mapa, victimas)
    
    assert resultado.rescatadas == 1, "Debería haber rescatado a la víctima V1"
    assert resultado.ticks_totales == 1, "Debería haber tomado exactamente 1 tick"
    assert resultado.nodos_expandidos > 0, "Debería haber expandido nodos"
    assert resultado.tiempo_segundos > 0, "El tiempo debe ser mayor a 0"
    print(f" [OK] {resultado}")


def test_bfs_mapa_proyecto():
    print("\n--- 2. Probando BFS con los archivos del proyecto (data/mapa.txt) ---")
    mapa = cargar_mapa("data/mapa.txt")
    victimas = cargar_victimas("data/victimas.txt", mapa)

    resultado = busqueda_amplitud(mapa, victimas)
    
    print("\n" + "="*50)
    print("           RESULTADO DE SIMULACIÓN (BFS)")
    print("="*50)
    print(f" Víctimas totales    : {resultado.victimas_totales}")
    print(f" Víctimas rescatadas : {resultado.rescatadas}")
    print(f" Víctimas fallecidas : {resultado.fallecidas}")
    print(f" Ticks totales       : {resultado.ticks_totales}")
    print(f" Nodos expandidos    : {resultado.nodos_expandidos}")
    print(f" Tiempo transcurrido : {resultado.tiempo_segundos:.4f}s")
    print("="*50)

    print("\nRuta encontrada (paso a paso):")
    for paso, (accion, r, c) in enumerate(resultado.camino):
        if paso == 0:
            print(f" Tick 0 (Inicio): Agente en ({r}, {c})")
        else:
            print(f" Tick {paso} ({accion}) -> ({r}, {c})")

    assert resultado.rescatadas > 0, "BFS debería ser capaz de rescatar al menos 1 víctima"
    print("\n [OK] BFS completó la búsqueda del mapa del proyecto sin bucles infinitos.")


if __name__ == "__main__":
    test_bfs_mapa_pequeno()
    test_bfs_mapa_proyecto()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 2.1 PASARON CON ÉXITO! <<<")
