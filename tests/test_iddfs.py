"""
Pruebas de validación para el algoritmo de Búsqueda en Profundidad Iterativa - IDDFS (Tarjeta 2.3).
"""

# Clases del modelo usadas en las pruebas.
from src.models import Mapa, Victima
# Funciones que leen los archivos de datos.
from src.loader import cargar_mapa, cargar_victimas
# El algoritmo que se prueba.
from src.algorithms.iddfs import busqueda_profundidad_iterativa

# Prueba 1: IDDFS en un mapa mínimo con una sola víctima.
def test_iddfs_mapa_pequeno():
    # Mensaje informativo.
    print("--- 1. Probando IDDFS en mapa pequeño (3x3 con 1 víctima alcanzable) ---")
    # Mapa 3x3: el agente solo puede ir al este.
    mapa = Mapa(["###", "#S.", "###"], inicio=(1, 1))
    # Una víctima en (1,2) con 5 ticks de vida.
    victimas = {"V1": Victima("V1", 1, 2, 5)}

    # Ejecuta IDDFS con la cota por defecto (50).
    resultado = busqueda_profundidad_iterativa(mapa, victimas)
    
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


# Prueba 2: IDDFS con los archivos reales del proyecto.
def test_iddfs_mapa_proyecto():
    # Mensaje informativo.
    print("\n--- 2. Probando IDDFS con los archivos del proyecto (data/mapa.txt) ---")
    # Carga el mapa real.
    mapa = cargar_mapa("data/mapa.txt")
    # Carga las víctimas reales validándolas contra el mapa.
    victimas = cargar_victimas("data/victimas.txt", mapa)

    # Ejecuta IDDFS con la cota por defecto.
    resultado = busqueda_profundidad_iterativa(mapa, victimas)
    
    # Línea en blanco y barra de 50 "=".
    print("\n" + "="*50)
    # Título del reporte.
    print("           RESULTADO DE SIMULACIÓN (IDDFS)")
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
    # Tiempo en segundos.
    print(f" Tiempo transcurrido : {resultado.tiempo_segundos:.4f}s")
    # Barra de cierre.
    print("="*50)

    # Encabezado de la ruta.
    print("\nRuta encontrada (paso a paso):")
    # Recorre la ruta con su número de paso.
    for paso, (accion, r, c) in enumerate(resultado.camino):
        # Paso 0 = estado inicial.
        if paso == 0:
            print(f" Tick 0 (Inicio): Agente en ({r}, {c})")
        # Los demás pasos muestran acción y celda destino.
        else:
            print(f" Tick {paso} ({accion}) -> ({r}, {c})")

    # IDDFS debe rescatar al menos 1 víctima.
    assert resultado.rescatadas > 0, "IDDFS debería rescatar al menos 1 víctima"
    # Mensaje de éxito.
    print("\n [OK] IDDFS completó la búsqueda del mapa del proyecto con éxito.")


# Ejecución directa del archivo.
if __name__ == "__main__":
    # Prueba 1.
    test_iddfs_mapa_pequeno()
    # Prueba 2.
    test_iddfs_mapa_proyecto()
    # Mensaje final.
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 2.3 PASARON CON ÉXITO! <<<")