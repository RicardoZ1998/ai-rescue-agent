from src.modelos_de_datos import MapaDelEntorno, VictimaEnRiesgo
from src.cargador_de_archivos import cargar_mapa_desde_archivo, cargar_victimas_desde_archivo
from src.algoritmos_de_busqueda.busqueda_en_profundidad_iterativa import ejecutar_busqueda_en_profundidad_iterativa

def test_iddfs_mapa_pequeno():
    print("--- 1. Probando IDDFS en mapa pequeño (3x3 con 1 víctima alcanzable) ---")
    mapa_de_prueba = MapaDelEntorno(["###", "#S.", "###"], posicion_de_inicio=(1, 1))
    diccionario_de_victimas = {"V1": VictimaEnRiesgo("V1", 1, 2, 5)}

    resultado_de_busqueda_iddfs = ejecutar_busqueda_en_profundidad_iterativa(mapa_de_prueba, diccionario_de_victimas)
    
    assert resultado_de_busqueda_iddfs.rescatadas == 1, "Debería haber rescatado a la víctima V1"
    assert resultado_de_busqueda_iddfs.ticks_totales == 1, "Debería haber tomado exactamente 1 tick"
    assert resultado_de_busqueda_iddfs.nodos_expandidos > 0, "Debería haber expandido nodos"
    assert resultado_de_busqueda_iddfs.tiempo_segundos > 0, "El tiempo debe ser mayor a 0"
    print(f" [OK] {resultado_de_busqueda_iddfs}")


def test_iddfs_mapa_proyecto():
    print("\n--- 2. Probando IDDFS con los archivos del proyecto (data/mapa.txt) ---")
    mapa_de_prueba = cargar_mapa_desde_archivo("data/mapa.txt")
    diccionario_de_victimas = cargar_victimas_desde_archivo("data/victimas.txt", mapa_de_prueba)

    resultado_de_busqueda_iddfs = ejecutar_busqueda_en_profundidad_iterativa(mapa_de_prueba, diccionario_de_victimas)
    
    print("\n" + "="*50)
    print("           RESULTADO DE SIMULACIÓN (IDDFS)")
    print("="*50)
    print(f" Víctimas totales    : {resultado_de_busqueda_iddfs.victimas_totales}")
    print(f" Víctimas rescatadas : {resultado_de_busqueda_iddfs.rescatadas}")
    print(f" Víctimas fallecidas : {resultado_de_busqueda_iddfs.fallecidas}")
    print(f" Ticks totales       : {resultado_de_busqueda_iddfs.ticks_totales}")
    print(f" Nodos expandidos    : {resultado_de_busqueda_iddfs.nodos_expandidos}")
    print(f" Tiempo transcurrido : {resultado_de_busqueda_iddfs.tiempo_segundos:.4f}s")
    print("="*50)

    print("\nRuta encontrada (paso a paso):")
    for numero_de_paso, (accion_realizada, fila_del_agente, columna_del_agente) in enumerate(resultado_de_busqueda_iddfs.camino):
        if numero_de_paso == 0:
            print(f" Tick 0 (Inicio): Agente en ({fila_del_agente}, {columna_del_agente})")
        else:
            print(f" Tick {numero_de_paso} ({accion_realizada}) -> ({fila_del_agente}, {columna_del_agente})")

    assert resultado_de_busqueda_iddfs.rescatadas > 0, "IDDFS debería rescatar al menos 1 víctima"
    print("\n [OK] IDDFS completó la búsqueda del mapa del proyecto con éxito.")


if __name__ == "__main__":
    test_iddfs_mapa_pequeno()
    test_iddfs_mapa_proyecto()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 2.3 PASARON CON ÉXITO! <<<")
