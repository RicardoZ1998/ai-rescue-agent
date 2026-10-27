"""
Pruebas de validación para la clase Estado (Tarjeta 1.2).
"""

from src.models import Mapa, Victima, Estado

def test_estado_hasheable():
    print("--- 1. Probando hashing e inmutabilidad en Set ---")
    e1 = Estado(1, 1, frozenset(["V1", "V2"]), tick_actual=0)
    e2 = Estado(1, 1, frozenset(["V1", "V2"]), tick_actual=0)
    e3 = Estado(1, 2, frozenset(["V1"]), tick_actual=1)

    visitados = set()
    visitados.add(e1)

    assert e1 == e2, "e1 y e2 deberían ser iguales"
    assert e2 in visitados, "e2 debería ser reconocido como ya visitado en el set"
    assert e3 not in visitados, "e3 no debería estar en el set"
    print(" [OK] Estado es hasheable y compatible con set() de visitados.")


def test_generacion_sucesores():
    print("\n--- 2. Probando generación de sucesores y restricciones de pared ---")
    # Mini mapa 3x3:
    # ###
    # #S.
    # ###
    celdas = [
        "###",
        "#S.",
        "###"
    ]
    mapa = Mapa(celdas, inicio=(1, 1))
    
    # Víctima V1 en (1, 2) con 1 tick de vida
    dict_victimas = {
        "V1": Victima("V1", fila=1, columna=2, ticks_supervivencia=1)
    }

    estado_inicial = Estado(
        fila=1,
        columna=1,
        victimas_vivas=frozenset(["V1"]),
        tick_actual=0
    )

    sucesores = estado_inicial.generar_sucesores(mapa, dict_victimas)
    
    # Solo puede moverse al Este hacia (1, 2), ya que Norte, Sur y Oeste son '#'
    assert len(sucesores) == 1, f"Debería haber solo 1 sucesor válido, pero hay {len(sucesores)}"
    
    sucesor_este = sucesores[0]
    print(f"Sucesor generado: {sucesor_este}")
    assert sucesor_este.accion == 'E', "La acción debería ser 'E'"
    assert sucesor_este.fila == 1 and sucesor_este.columna == 2, "La nueva posición debe ser (1, 2)"
    assert sucesor_este.tick_actual == 1, "El tick actual debe ser 1"
    assert "V1" in sucesor_este.victimas_rescatadas, "V1 debió haber sido rescatada"
    assert len(sucesor_este.victimas_vivas) == 0, "No deberían quedar víctimas pendientes por rescatar"
    print(" [OK] Restricciones de pared y rescate en tick validado exitosamente.")


def test_muerte_por_tiempo():
    print("\n--- 3. Probando muerte de víctima por expiración de ticks ---")
    celdas = [
        "...",
        ".S.",
        "..."
    ]
    mapa = Mapa(celdas, inicio=(1, 1))

    # Víctima V_lejos en (0, 0) que expira en tick 0 (ya no alcanzable en tick 1)
    dict_victimas = {
        "V_lejos": Victima("V_lejos", fila=0, columna=0, ticks_supervivencia=0)
    }

    estado_inicial = Estado(
        fila=1,
        columna=1,
        victimas_vivas=frozenset(["V_lejos"]),
        tick_actual=0
    )

    sucesores = estado_inicial.generar_sucesores(mapa, dict_victimas)
    # Al dar un paso a cualquier dirección, el tick pasa a 1, por lo que V_lejos muere
    for suc in sucesores:
        assert "V_lejos" not in suc.victimas_vivas, "La víctima debía morir al pasar a tick 1"
        assert "V_lejos" not in suc.victimas_rescatadas, "La víctima no fue rescatada"
    print(" [OK] Las víctimas mueren correctamente cuando tick_actual > ticks_supervivencia.")


if __name__ == "__main__":
    test_estado_hasheable()
    test_generacion_sucesores()
    test_muerte_por_tiempo()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 1.2 PASARON CON ÉXITO! <<<")
