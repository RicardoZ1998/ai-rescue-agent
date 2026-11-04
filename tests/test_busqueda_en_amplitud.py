from src.modelos_de_datos import MapaDelEntorno, VictimaEnRiesgo
from src.cargador_de_archivos import cargar_mapa_desde_archivo, cargar_victimas_desde_archivo
from src.algoritmos_de_busqueda.busqueda_en_amplitud import ejecutar_busqueda_en_amplitud

def test_bfs_mapa_pequeno():
    print("--- 1. Probando BFS en mapa pequeño (3x3 con 1 víctima alcanzable) ---")
    mapa_de_prueba = MapaDelEntorno(["###", "#S.", "###"], posicion_de_inicio=(1, 1))
    diccionario_de_victimas = {"V1": VictimaEnRiesgo("V1", 1, 2, 5)}

    resultado_de_busqueda_bfs = ejecutar_busqueda_en_amplitud(mapa_de_prueba, diccionario_de_victimas)
    
    assert resultado_de_busqueda_bfs.rescatadas == 1, "Debería haber rescatado a la víctima V1"
    assert resultado_de_busqueda_bfs.ticks_totales == 1, "Debería haber tomado exactamente 1 tick"
    assert resultado_de_busqueda_bfs.nodos_expandidos > 0, "Debería haber expandido nodos"
    assert resultado_de_busqueda_bfs.tiempo_segundos > 0, "El tiempo debe ser mayor a 0"
    print(f" [OK] {resultado_de_busqueda_bfs}")


def test_bfs_mapa_proyecto():
    print("\n--- 2. Probando BFS con los archivos del proyecto (data/mapa.txt) ---")
    mapa_de_prueba = cargar_mapa_desde_archivo("data/mapa.txt")
    diccionario_de_victimas = cargar_victimas_desde_archivo("data/victimas.txt", mapa_de_prueba)

    resultado_de_busqueda_bfs = ejecutar_busqueda_en_amplitud(mapa_de_prueba, diccionario_de_victimas)
    
    print("\n" + "="*50)
    print("           RESULTADO DE SIMULACIÓN (BFS)")
    print("="*50)
    print(f" Víctimas totales    : {resultado_de_busqueda_bfs.victimas_totales}")
    print(f" Víctimas rescatadas : {resultado_de_busqueda_bfs.rescatadas}")
    print(f" Víctimas fallecidas : {resultado_de_busqueda_bfs.fallecidas}")
    print(f" Ticks totales       : {resultado_de_busqueda_bfs.ticks_totales}")
    print(f" Nodos expandidos    : {resultado_de_busqueda_bfs.nodos_expandidos}")
    print(f" Tiempo transcurrido : {resultado_de_busqueda_bfs.tiempo_segundos:.4f}s")
    print("="*50)

    print("\nRuta encontrada (paso a paso):")
    for numero_de_paso, (accion_realizada, fila_del_agente, columna_del_agente) in enumerate(resultado_de_busqueda_bfs.camino):
        if numero_de_paso == 0:
            print(f" Tick 0 (Inicio): Agente en ({fila_del_agente}, {columna_del_agente})")
        else:
            print(f" Tick {numero_de_paso} ({accion_realizada}) -> ({fila_del_agente}, {columna_del_agente})")

    assert resultado_de_busqueda_bfs.rescatadas > 0, "BFS debería ser capaz de rescatar al menos 1 víctima"
    print("\n [OK] BFS completó la búsqueda del mapa del proyecto sin bucles infinitos.")


if __name__ == "__main__":
    test_bfs_mapa_pequeno()
    test_bfs_mapa_proyecto()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 2.1 PASARON CON ÉXITO! <<<")
