"""
Pruebas de validación para el algoritmo de Búsqueda de Costo Uniforme - UCS (Tarjeta 2.2).
"""

from src.models import Mapa, Victima
from src.loader import cargar_mapa, cargar_victimas
from src.algorithms.ucs import busqueda_costo_uniforme

def test_ucs_mapa_pequeno():
    print("--- 1. Probando UCS en mapa pequeño (3x3 con 1 víctima alcanzable) ---")
    mapa = Mapa(["###", "#S.", "###"], inicio=(1, 1))
    victimas = {"V1": Victima("V1", 1, 2, 5)}

    resultado = busqueda_costo_uniforme(mapa, victimas)
    
    assert resultado.rescatadas == 1, "Debería haber rescatado a la víctima V1"
    assert resultado.ticks_totales == 1, "Debería haber tomado exactamente 1 tick"
    assert resultado.nodos_expandidos > 0, "Debería haber expandido nodos"
    assert resultado.tiempo_segundos > 0, "El tiempo debe ser mayor a 0"
    print(f" [OK] {resultado}")


def test_ucs_mapa_proyecto():
    print("\n--- 2. Probando UCS con los archivos del proyecto (data/mapa.txt) ---")
    mapa = cargar_mapa("data/mapa.txt")
    victimas = cargar_victimas("data/victimas.txt", mapa)

    resultado = busqueda_costo_uniforme(mapa, victimas)
    
    print("\n" + "="*50)
    print("           RESULTADO DE SIMULACIÓN (UCS)")
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

    assert resultado.rescatadas > 0, "UCS debería ser capaz de rescatar al menos 1 víctima"
    print("\n [OK] UCS completó la búsqueda del mapa del proyecto con éxito.")


if __name__ == "__main__":
    test_ucs_mapa_pequeno()
    test_ucs_mapa_proyecto()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 2.2 PASARON CON ÉXITO! <<<")

