"""
Pruebas de validación para la clase Estado (Tarjeta 1.2).
"""

# Importa las 3 clases del modelo que se van a probar/usar.
from src.models import Mapa, Victima, Estado

# Prueba 1: verifica que Estado se puede usar en un set (hash + igualdad correctos).
def test_estado_hasheable():
    # Mensaje informativo en consola.
    print("--- 1. Probando hashing e inmutabilidad en Set ---")
    # e1: agente en (1,1), víctimas vivas V1 y V2, tick 0.
    e1 = Estado(1, 1, frozenset(["V1", "V2"]), tick_actual=0)
    # e2: idéntico a e1 pero es OTRO objeto distinto en memoria.
    e2 = Estado(1, 1, frozenset(["V1", "V2"]), tick_actual=0)
    # e3: distinto a e1 (otra columna, solo V1 viva, tick 1).
    e3 = Estado(1, 2, frozenset(["V1"]), tick_actual=1)

    # Conjunto vacío de "visitados".
    visitados = set()
    # Mete e1 en el conjunto.
    visitados.add(e1)

    # e1 y e2 deben ser iguales por valor (usa __eq__).
    assert e1 == e2, "e1 y e2 deberían ser iguales"
    # e2 debe "estar" en el set aunque sea otro objeto (usa __hash__ y __eq__).
    assert e2 in visitados, "e2 debería ser reconocido como ya visitado en el set"
    # e3 no debe estar en el set porque es un estado distinto.
    assert e3 not in visitados, "e3 no debería estar en el set"
    # Mensaje de éxito.
    print(" [OK] Estado es hasheable y compatible con set() de visitados.")


# Prueba 2: verifica la generación de sucesores respetando paredes y el rescate.
def test_generacion_sucesores():
    # Mensaje informativo (el \n deja una línea en blanco antes).
    print("\n--- 2. Probando generación de sucesores y restricciones de pared ---")
    # Mini mapa 3x3:
    # ###
    # #S.
    # ###
    # Mapa de prueba: el agente solo puede moverse hacia el este.
    celdas = [
        "###",
        "#S.",
        "###"
    ]
    # Crea el mapa con inicio en (1, 1).
    mapa = Mapa(celdas, inicio=(1, 1))
    
    # Víctima V1 en (1, 2) con 1 tick de vida
    # Diccionario con una sola víctima: justo al este del agente, con 1 tick de vida.
    dict_victimas = {
        "V1": Victima("V1", fila=1, columna=2, ticks_supervivencia=1)
    }

    # Estado inicial: agente en (1,1), V1 viva, tick 0.
    estado_inicial = Estado(
        # Fila del agente.
        fila=1,
        # Columna del agente.
        columna=1,
        # V1 está viva.
        victimas_vivas=frozenset(["V1"]),
        # Tick 0.
        tick_actual=0
    )

    # Genera los sucesores del estado inicial.
    sucesores = estado_inicial.generar_sucesores(mapa, dict_victimas)
    
    # Solo puede moverse al Este hacia (1, 2), ya que Norte, Sur y Oeste son '#'
    # Debe haber exactamente 1 sucesor (los otros 3 movimientos chocan con paredes).
    assert len(sucesores) == 1, f"Debería haber solo 1 sucesor válido, pero hay {len(sucesores)}"
    
    # Toma el único sucesor.
    sucesor_este = sucesores[0]
    # Lo imprime para inspección visual.
    print(f"Sucesor generado: {sucesor_este}")
    # La acción debe ser 'E' (Este).
    assert sucesor_este.accion == 'E', "La acción debería ser 'E'"
    # La nueva posición debe ser (1, 2).
    assert sucesor_este.fila == 1 and sucesor_este.columna == 2, "La nueva posición debe ser (1, 2)"
    # El tick debe haber subido a 1.
    assert sucesor_este.tick_actual == 1, "El tick actual debe ser 1"
    # V1 debe estar rescatada (llegó en el tick 1, que es <= su límite de 1).
    assert "V1" in sucesor_este.victimas_rescatadas, "V1 debió haber sido rescatada"
    # Ya no deben quedar víctimas vivas pendientes.
    assert len(sucesor_este.victimas_vivas) == 0, "No deberían quedar víctimas pendientes por rescatar"
    # Mensaje de éxito.
    print(" [OK] Restricciones de pared y rescate en tick validado exitosamente.")


# Prueba 3: verifica que una víctima muere cuando se le acaba el tiempo.
def test_muerte_por_tiempo():
    # Mensaje informativo.
    print("\n--- 3. Probando muerte de víctima por expiración de ticks ---")
    # Mapa 3x3 sin paredes (el agente puede ir en las 4 direcciones).
    celdas = [
        "...",
        ".S.",
        "..."
    ]
    # Crea el mapa con inicio en el centro (1, 1).
    mapa = Mapa(celdas, inicio=(1, 1))

    # Víctima V_lejos en (0, 0) que expira en tick 0 (ya no alcanzable en tick 1)
    # Víctima en la esquina con 0 ticks de vida: muere apenas pase el primer tick.
    dict_victimas = {
        "V_lejos": Victima("V_lejos", fila=0, columna=0, ticks_supervivencia=0)
    }

    # Estado inicial con V_lejos viva en tick 0.
    estado_inicial = Estado(
        # Fila del agente.
        fila=1,
        # Columna del agente.
        columna=1,
        # V_lejos viva.
        victimas_vivas=frozenset(["V_lejos"]),
        # Tick 0.
        tick_actual=0
    )

    # Genera los 4 sucesores posibles.
    sucesores = estado_inicial.generar_sucesores(mapa, dict_victimas)
    # Al dar un paso a cualquier dirección, el tick pasa a 1, por lo que V_lejos muere
    # Revisa cada sucesor.
    for suc in sucesores:
        # V_lejos ya no debe estar entre las vivas.
        assert "V_lejos" not in suc.victimas_vivas, "La víctima debía morir al pasar a tick 1"
        # Y tampoco entre las rescatadas (murió, no fue salvada).
        assert "V_lejos" not in suc.victimas_rescatadas, "La víctima no fue rescatada"
    # Mensaje de éxito.
    print(" [OK] Las víctimas mueren correctamente cuando tick_actual > ticks_supervivencia.")


# Esto se ejecuta solo si el archivo se corre directamente (python tests/test_estado.py).
if __name__ == "__main__":
    # Ejecuta la prueba 1.
    test_estado_hasheable()
    # Ejecuta la prueba 2.
    test_generacion_sucesores()
    # Ejecuta la prueba 3.
    test_muerte_por_tiempo()
    # Mensaje final si ninguna aserción falló.
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 1.2 PASARON CON ÉXITO! <<<")