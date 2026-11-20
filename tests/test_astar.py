"""
Pruebas de validación para el algoritmo de Búsqueda Informada A* (Tarjeta 3.2).
Incluye la tabla comparativa oficial entre los 4 algoritmos (BFS, UCS, IDDFS, A*).
"""

# Clases del modelo usadas en las pruebas.
from src.models import Mapa, Victima
# Funciones que leen los archivos de datos.
from src.loader import cargar_mapa, cargar_victimas
# Los 4 algoritmos (para la comparación final).
from src.algorithms.bfs import busqueda_amplitud
from src.algorithms.ucs import busqueda_costo_uniforme
from src.algorithms.iddfs import busqueda_profundidad_iterativa
from src.algorithms.astar import busqueda_a_estrella

# Prueba 1: A* en un mapa mínimo con una sola víctima.
def test_astar_mapa_pequeno():
    # Mensaje informativo.
    print("--- 1. Probando A* en mapa pequeño (3x3 con 1 víctima alcanzable) ---")
    # Mapa 3x3: el agente solo puede ir al este.
    mapa = Mapa(["###", "#S.", "###"], inicio=(1, 1))
    # Una víctima en (1,2) con 5 ticks de vida.
    victimas = {"V1": Victima("V1", 1, 2, 5)}

    # Ejecuta A*.
    resultado = busqueda_a_estrella(mapa, victimas)
    
    # Debe rescatar exactamente 1 víctima.
    assert resultado.rescatadas == 1, "Debería haber rescatado a la víctima V1"
    # Debe tardar exactamente 1 tick.
    assert resultado.ticks_totales == 1, "Debería haber tomado exactamente 1 tick"
    # Debe haber expandido al menos 1 nodo.
    assert resultado.nodos_expandidos > 0, "Debería haber expandido nodos"
    # El tiempo medido debe ser mayor que 0.
    assert resultado.tiempo_segundos > 0, "El tiempo debe ser mayor a 0"
    # Imprime el resumen del resultado.
    print(f" [OK] {resultado}")


# Prueba 2: A* con el mapa oficial; verifica el resultado esperado (3 rescatadas en 14 ticks).
def test_astar_mapa_proyecto():
    # Mensaje informativo.
    print("\n--- 2. Probando A* con el mapa oficial del proyecto (data/mapa.txt) ---")
    # Carga el mapa real.
    mapa = cargar_mapa("data/mapa.txt")
    # Carga las víctimas reales validándolas contra el mapa.
    victimas = cargar_victimas("data/victimas.txt", mapa)

    # Ejecuta A*.
    res_astar = busqueda_a_estrella(mapa, victimas)
    
    # Línea en blanco y barra de 50 "=".
    print("\n" + "="*50)
    # Título del reporte.
    print("           RESULTADO DE SIMULACIÓN (A*)")
    # Barra de cierre del encabezado.
    print("="*50)
    # Total de víctimas.
    print(f" Víctimas totales    : {res_astar.victimas_totales}")
    # Rescatadas.
    print(f" Víctimas rescatadas : {res_astar.rescatadas}")
    # Fallecidas.
    print(f" Víctimas fallecidas : {res_astar.fallecidas}")
    # Ticks totales.
    print(f" Ticks totales       : {res_astar.ticks_totales}")
    # Nodos expandidos.
    print(f" Nodos expandidos    : {res_astar.nodos_expandidos}")
    # Tiempo en segundos.
    print(f" Tiempo transcurrido : {res_astar.tiempo_segundos:.4f}s")
    # Barra de cierre.
    print("="*50)

    # Encabezado de la ruta.
    print("\nRuta encontrada (paso a paso):")
    # Recorre la ruta con su número de paso.
    for paso, (accion, r, c) in enumerate(res_astar.camino):
        # Paso 0 = estado inicial.
        if paso == 0:
            print(f" Tick 0 (Inicio): Agente en ({r}, {c})")
        # Los demás pasos muestran acción y celda destino.
        else:
            print(f" Tick {paso} ({accion}) -> ({r}, {c})")

    # En el mapa oficial, A* debe rescatar exactamente 3 víctimas.
    assert res_astar.rescatadas == 3, f"A* debió rescatar 3 víctimas, rescató {res_astar.rescatadas}"
    # Y debe lograrlo en 14 ticks (la ruta óptima esperada).
    assert res_astar.ticks_totales == 14, f"A* debió encontrar la ruta óptima de 14 ticks, obtuvo {res_astar.ticks_totales}"


# Prueba 3: comparación de los 4 algoritmos sobre el mapa oficial.
def test_comparacion_4_algoritmos():
    # Línea en blanco y barra de 60 "=".
    print("\n" + "="*60)
    # Título de la tabla.
    print("        TABLA COMPARATIVA DE LOS 4 ALGORITMOS")
    # Barra de cierre.
    print("="*60)
    # Carga el mapa real.
    mapa = cargar_mapa("data/mapa.txt")
    # Carga las víctimas reales.
    victimas = cargar_victimas("data/victimas.txt", mapa)

    # Ejecuta BFS.
    res_bfs = busqueda_amplitud(mapa, victimas)
    # Ejecuta UCS.
    res_ucs = busqueda_costo_uniforme(mapa, victimas)
    # Ejecuta IDDFS con cota máxima de 16.
    res_iddfs = busqueda_profundidad_iterativa(mapa, victimas, limite_maximo_cota=16)
    # Ejecuta A*.
    res_astar = busqueda_a_estrella(mapa, victimas)

    # Lista con los 4 resultados para imprimirlos en tabla.
    resultados = [res_bfs, res_ucs, res_iddfs, res_astar]

    # Encabezado de la tabla; "<10" alinea el texto a la izquierda en un ancho de 10 caracteres.
    print(f"{'Algoritmo':<10} | {'Nodos':<8} | {'Tiempo':<10} | {'Rescatadas':<10} | {'Fallecidas':<10} | {'Ticks':<6}")
    # Línea separadora de 68 guiones.
    print("-" * 68)
    # Imprime una fila por algoritmo.
    for r in resultados:
        print(f"{r.algoritmo:<10} | {r.nodos_expandidos:<8} | {r.tiempo_segundos:.4f}s   | {r.rescatadas:<10} | {r.fallecidas:<10} | {r.ticks_totales:<6}")
    # Línea de cierre de 68 "=".
    print("=" * 68)

    # Validar que A* explore significativamente menos nodos que BFS y UCS
    # Comprueba que A* expandió menos nodos que BFS (con mensaje de error descriptivo si falla).
    assert res_astar.nodos_expandidos < res_bfs.nodos_expandidos, (
        f"A* debería expandir menos nodos ({res_astar.nodos_expandidos}) que BFS ({res_bfs.nodos_expandidos})"
    )
    # Mensaje de éxito con la comparación de nodos.
    print(f"\n [OK] Demostrado: A* exploró {res_astar.nodos_expandidos} nodos frente a {res_bfs.nodos_expandidos} de BFS.")


# Ejecución directa del archivo.
if __name__ == "__main__":
    # Prueba 1.
    test_astar_mapa_pequeno()
    # Prueba 2.
    test_astar_mapa_proyecto()
    # Prueba 3.
    test_comparacion_4_algoritmos()
    # Mensaje final.
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 3.2 PASARON CON ÉXITO! <<<")