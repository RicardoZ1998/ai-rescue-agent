from src.modelos_de_datos import MapaDelEntorno, VictimaEnRiesgo, EstadoDelAgente

def test_estado_hasheable():
    print("--- 1. Probando hashing e inmutabilidad en Set ---")
    estado_primero = EstadoDelAgente(1, 1, frozenset(["V1", "V2"]), tick_actual=0)
    estado_identico_al_primero = EstadoDelAgente(1, 1, frozenset(["V1", "V2"]), tick_actual=0)
    estado_diferente = EstadoDelAgente(1, 2, frozenset(["V1"]), tick_actual=1)

    conjunto_de_estados_visitados = set()
    conjunto_de_estados_visitados.add(estado_primero)

    assert estado_primero == estado_identico_al_primero, "estado_primero y estado_identico_al_primero deberían ser iguales"
    assert estado_identico_al_primero in conjunto_de_estados_visitados, "estado_identico_al_primero debería ser reconocido como ya visitado en el set"
    assert estado_diferente not in conjunto_de_estados_visitados, "estado_diferente no debería estar en el set"
    print(" [OK] Estado es hasheable y compatible con set() de visitados.")


def test_generacion_sucesores():
    print("\n--- 2. Probando generación de sucesores y restricciones de pared ---")
    celdas_del_mapa = [
        "###",
        "#S.",
        "###"
    ]
    mapa_de_prueba = MapaDelEntorno(celdas_del_mapa, posicion_de_inicio=(1, 1))
    
    diccionario_de_victimas = {
        "V1": VictimaEnRiesgo("V1", fila=1, columna=2, ticks_supervivencia=1)
    }

    estado_inicial_de_prueba = EstadoDelAgente(
        fila_actual=1,
        columna_actual=1,
        conjunto_de_victimas_vivas=frozenset(["V1"]),
        tick_actual=0
    )

    lista_de_sucesores_generados = estado_inicial_de_prueba.generar_estados_sucesores(mapa_de_prueba, diccionario_de_victimas)
    
    assert len(lista_de_sucesores_generados) == 1, f"Debería haber solo 1 sucesor válido, pero hay {len(lista_de_sucesores_generados)}"
    
    unico_sucesor_hacia_el_este = lista_de_sucesores_generados[0]
    print(f"Sucesor generado: {unico_sucesor_hacia_el_este}")
    assert unico_sucesor_hacia_el_este.accion_origen == 'Este', "La acción debería ser 'Este'"
    assert unico_sucesor_hacia_el_este.fila == 1 and unico_sucesor_hacia_el_este.columna == 2, "La nueva posición debe ser (1, 2)"
    assert unico_sucesor_hacia_el_este.tick_actual == 1, "El tick actual debe ser 1"
    assert "V1" in unico_sucesor_hacia_el_este.victimas_rescatadas, "V1 debió haber sido rescatada"
    assert len(unico_sucesor_hacia_el_este.victimas_vivas) == 0, "No deberían quedar víctimas pendientes por rescatar"
    print(" [OK] Restricciones de pared y rescate en tick validado exitosamente.")


def test_muerte_por_tiempo():
    print("\n--- 3. Probando muerte de víctima por expiración de ticks ---")
    celdas_del_mapa = [
        "...",
        ".S.",
        "..."
    ]
    mapa_de_prueba = MapaDelEntorno(celdas_del_mapa, posicion_de_inicio=(1, 1))

    diccionario_de_victimas = {
        "V_lejos": VictimaEnRiesgo("V_lejos", fila=0, columna=0, ticks_supervivencia=0)
    }

    estado_inicial_de_prueba = EstadoDelAgente(
        fila_actual=1,
        columna_actual=1,
        conjunto_de_victimas_vivas=frozenset(["V_lejos"]),
        tick_actual=0
    )

    lista_de_sucesores_generados = estado_inicial_de_prueba.generar_estados_sucesores(mapa_de_prueba, diccionario_de_victimas)
    for estado_sucesor in lista_de_sucesores_generados:
        assert "V_lejos" not in estado_sucesor.victimas_vivas, "La víctima debía morir al pasar a tick 1"
        assert "V_lejos" not in estado_sucesor.victimas_rescatadas, "La víctima no fue rescatada"
    print(" [OK] Las víctimas mueren correctamente cuando tick_actual > ticks_supervivencia.")


if __name__ == "__main__":
    test_estado_hasheable()
    test_generacion_sucesores()
    test_muerte_por_tiempo()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 1.2 PASARON CON ÉXITO! <<<")
