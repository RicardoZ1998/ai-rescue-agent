from src.modelos_de_datos import MapaDelEntorno, VictimaEnRiesgo
from src.cargador_de_archivos import cargar_mapa_desde_archivo, cargar_victimas_desde_archivo
from src.algoritmos_de_busqueda.busqueda_en_amplitud import ejecutar_busqueda_en_amplitud
from src.algoritmos_de_busqueda.busqueda_de_costo_uniforme import ejecutar_busqueda_de_costo_uniforme
from src.algoritmos_de_busqueda.busqueda_en_profundidad_iterativa import ejecutar_busqueda_en_profundidad_iterativa
from src.algoritmos_de_busqueda.busqueda_a_estrella import ejecutar_busqueda_a_estrella

def test_astar_mapa_pequeno():
    print("--- 1. Probando A* en mapa pequeño (3x3 con 1 víctima alcanzable) ---")
    mapa_de_prueba = MapaDelEntorno(["###", "#S.", "###"], posicion_de_inicio=(1, 1))
    diccionario_de_victimas = {"V1": VictimaEnRiesgo("V1", 1, 2, 5)}

    resultado_de_busqueda_astar = ejecutar_busqueda_a_estrella(mapa_de_prueba, diccionario_de_victimas)
    
    assert resultado_de_busqueda_astar.rescatadas == 1, "Debería haber rescatado a la víctima V1"
    assert resultado_de_busqueda_astar.ticks_totales == 1, "Debería haber tomado exactamente 1 tick"
    assert resultado_de_busqueda_astar.nodos_expandidos > 0, "Debería haber expandido nodos"
    assert resultado_de_busqueda_astar.tiempo_segundos > 0, "El tiempo debe ser mayor a 0"
    print(f" [OK] {resultado_de_busqueda_astar}")


def test_astar_mapa_proyecto():
    print("\n--- 2. Probando A* con el mapa oficial del proyecto (data/mapa.txt) ---")
    mapa_de_prueba = cargar_mapa_desde_archivo("data/mapa.txt")
    diccionario_de_victimas = cargar_victimas_desde_archivo("data/victimas.txt", mapa_de_prueba)

    resultado_de_busqueda_astar = ejecutar_busqueda_a_estrella(mapa_de_prueba, diccionario_de_victimas)
    
    print("\n" + "="*50)
    print("           RESULTADO DE SIMULACIÓN (A*)")
    print("="*50)
    print(f" Víctimas totales    : {resultado_de_busqueda_astar.victimas_totales}")
    print(f" Víctimas rescatadas : {resultado_de_busqueda_astar.rescatadas}")
    print(f" Víctimas fallecidas : {resultado_de_busqueda_astar.fallecidas}")
    print(f" Ticks totales       : {resultado_de_busqueda_astar.ticks_totales}")
    print(f" Nodos expandidos    : {resultado_de_busqueda_astar.nodos_expandidos}")
    print(f" Tiempo transcurrido : {resultado_de_busqueda_astar.tiempo_segundos:.4f}s")
    print("="*50)

    print("\nRuta encontrada (paso a paso):")
    for numero_de_paso, (accion_realizada, fila_del_agente, columna_del_agente) in enumerate(resultado_de_busqueda_astar.camino):
        if numero_de_paso == 0:
            print(f" Tick 0 (Inicio): Agente en ({fila_del_agente}, {columna_del_agente})")
        else:
            print(f" Tick {numero_de_paso} ({accion_realizada}) -> ({fila_del_agente}, {columna_del_agente})")

    assert resultado_de_busqueda_astar.rescatadas == 3, f"A* debió rescatar 3 víctimas, rescató {resultado_de_busqueda_astar.rescatadas}"
    assert resultado_de_busqueda_astar.ticks_totales == 14, f"A* debió encontrar la ruta óptima de 14 ticks, obtuvo {resultado_de_busqueda_astar.ticks_totales}"


def test_comparacion_4_algoritmos():
    print("\n" + "="*60)
    print("        TABLA COMPARATIVA DE LOS 4 ALGORITMOS")
    print("="*60)
    mapa_de_prueba = cargar_mapa_desde_archivo("data/mapa.txt")
    diccionario_de_victimas = cargar_victimas_desde_archivo("data/victimas.txt", mapa_de_prueba)

    resultado_de_busqueda_bfs = ejecutar_busqueda_en_amplitud(mapa_de_prueba, diccionario_de_victimas)
    resultado_de_busqueda_ucs = ejecutar_busqueda_de_costo_uniforme(mapa_de_prueba, diccionario_de_victimas)
    resultado_de_busqueda_iddfs = ejecutar_busqueda_en_profundidad_iterativa(mapa_de_prueba, diccionario_de_victimas, limite_maximo_cota=16)
    resultado_de_busqueda_astar = ejecutar_busqueda_a_estrella(mapa_de_prueba, diccionario_de_victimas)

    lista_de_todos_los_resultados = [resultado_de_busqueda_bfs, resultado_de_busqueda_ucs, resultado_de_busqueda_iddfs, resultado_de_busqueda_astar]

    print(f"{'Algoritmo':<10} | {'Nodos':<8} | {'Tiempo':<10} | {'Rescatadas':<10} | {'Fallecidas':<10} | {'Ticks':<6}")
    print("-" * 68)
    for resultado_actual in lista_de_todos_los_resultados:
        print(f"{resultado_actual.algoritmo:<10} | {resultado_actual.nodos_expandidos:<8} | {resultado_actual.tiempo_segundos:.4f}s   | {resultado_actual.rescatadas:<10} | {resultado_actual.fallecidas:<10} | {resultado_actual.ticks_totales:<6}")
    print("=" * 68)

    assert resultado_de_busqueda_astar.nodos_expandidos < resultado_de_busqueda_bfs.nodos_expandidos, (
        f"A* debería expandir menos nodos ({resultado_de_busqueda_astar.nodos_expandidos}) que BFS ({resultado_de_busqueda_bfs.nodos_expandidos})"
    )
    print(f"\n [OK] Demostrado: A* exploró {resultado_de_busqueda_astar.nodos_expandidos} nodos frente a {resultado_de_busqueda_bfs.nodos_expandidos} de BFS.")


if __name__ == "__main__":
    test_astar_mapa_pequeno()
    test_astar_mapa_proyecto()
    test_comparacion_4_algoritmos()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 3.2 PASARON CON ÉXITO! <<<")
