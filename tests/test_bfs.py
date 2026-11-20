"""
Pruebas de validación para el algoritmo de Búsqueda en Amplitud - BFS (Tarjeta 2.1).
"""

# Clases del modelo (Estado se importa pero no se usa en este archivo).
from src.models import Mapa, Victima, Estado
# Funciones que leen los archivos mapa.txt y victimas.txt.
from src.loader import cargar_mapa, cargar_victimas
# El algoritmo que se prueba.
from src.algorithms.bfs import busqueda_amplitud

# Prueba 1: BFS en un mapa mínimo con una sola víctima.
def test_bfs_mapa_pequeno():
    # Mensaje informativo.
    print("--- 1. Probando BFS en mapa pequeño (3x3 con 1 víctima alcanzable) ---")
    # Mapa:
    # ###
    # #S.
    # ###
    # Víctima en (1, 2) con 5 ticks de vida (distancia 1)
    # Mapa 3x3 con inicio en (1,1); solo existe la celda libre de la derecha.
    mapa = Mapa(["###", "#S.", "###"], inicio=(1, 1))
    # Una víctima en (1,2) con 5 ticks de vida.
    victimas = {"V1": Victima("V1", 1, 2, 5)}

    # Ejecuta BFS.
    resultado = busqueda_amplitud(mapa, victimas)
    
    # Debe rescatar exactamente 1 víctima.
    assert resultado.rescatadas == 1, "Debería haber rescatado a la víctima V1"
    # Debe tardar exactamente 1 tick (un paso al este).
    assert resultado.ticks_totales == 1, "Debería haber tomado exactamente 1 tick"
    # Debe haber expandido al menos 1 nodo.
    assert resultado.nodos_expandidos > 0, "Debería haber expandido nodos"
    # El tiempo medido debe ser mayor que 0.
    assert resultado.tiempo_segundos > 0, "El tiempo debe ser mayor a 0"
    # Imprime el resumen del resultado (usa __repr__).
    print(f" [OK] {resultado}")


# Prueba 2: BFS con los archivos reales del proyecto.
def test_bfs_mapa_proyecto():
    # Mensaje informativo.
    print("\n--- 2. Probando BFS con los archivos del proyecto (data/mapa.txt) ---")
    # Carga el mapa real (ruta relativa: hay que correr desde la raíz del proyecto).
    mapa = cargar_mapa("data/mapa.txt")
    # Carga las víctimas reales validándolas contra el mapa.
    victimas = cargar_victimas("data/victimas.txt", mapa)

    # Ejecuta BFS.
    resultado = busqueda_amplitud(mapa, victimas)
    
    # Imprime una línea en blanco y una barra de 50 signos "=".
    print("\n" + "="*50)
    # Título del reporte.
    print("           RESULTADO DE SIMULACIÓN (BFS)")
    # Barra de cierre del encabezado.
    print("="*50)
    # Total de víctimas.
    print(f" Víctimas totales    : {resultado.victimas_totales}")
    # Rescatadas.
    print(f" Víctimas rescatadas : {resultado.rescatadas}")
    # Fallecidas.
    print(f" Víctimas fallecidas : {resultado.fallecidas}")
    # Ticks totales.
    print(f" Ticks totales       : {resultado.ticks_totales}")
    # Nodos expandidos.
    print(f" Nodos expandidos    : {resultado.nodos_expandidos}")
    # Tiempo en segundos con 4 decimales.
    print(f" Tiempo transcurrido : {resultado.tiempo_segundos:.4f}s")
    # Barra de cierre.
    print("="*50)

    # Encabezado de la ruta.
    print("\nRuta encontrada (paso a paso):")
    # Recorre la ruta con su número de paso (enumerate empieza en 0).
    for paso, (accion, r, c) in enumerate(resultado.camino):
        # El paso 0 es el estado inicial (no hay acción).
        if paso == 0:
            print(f" Tick 0 (Inicio): Agente en ({r}, {c})")
        # Los demás pasos muestran la acción y la celda a la que llegó el agente.
        else:
            print(f" Tick {paso} ({accion}) -> ({r}, {c})")

    # BFS debe lograr rescatar al menos a 1 víctima en el mapa real.
    assert resultado.rescatadas > 0, "BFS debería ser capaz de rescatar al menos 1 víctima"
    # Mensaje de éxito.
    print("\n [OK] BFS completó la búsqueda del mapa del proyecto sin bucles infinitos.")


# Ejecución directa del archivo.
if __name__ == "__main__":
    # Prueba 1.
    test_bfs_mapa_pequeno()
    # Prueba 2.
    test_bfs_mapa_proyecto()
    # Mensaje final.
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 2.1 PASARON CON ÉXITO! <<<")