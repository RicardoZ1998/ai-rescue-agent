from src.modelos_de_datos import EstadoDelAgente, VictimaEnRiesgo
from src.funciones_heuristicas import calcular_heuristica_de_victimas_condenadas, calcular_heuristica_para_busqueda_a_estrella

def test_heuristica_victimas_condenadas():
    print("--- 1. Probando cálculo de víctimas condenadas h(n) ---")
    posicion_inicial_del_agente = (1, 1)
    
    diccionario_de_victimas = {
        "V1": VictimaEnRiesgo("V1", 1, 4, ticks_supervivencia=5),
        "V2": VictimaEnRiesgo("V2", 5, 5, ticks_supervivencia=2)
    }

    estado_de_prueba = EstadoDelAgente(
        fila_actual=posicion_inicial_del_agente[0],
        columna_actual=posicion_inicial_del_agente[1],
        conjunto_de_victimas_vivas=frozenset(["V1", "V2"]),
        tick_actual=0
    )

    valor_heuristico_calculado = calcular_heuristica_de_victimas_condenadas(estado_de_prueba, diccionario_de_victimas)
    assert valor_heuristico_calculado == 1, f"Se esperaba 1 víctima condenada (V2), pero se obtuvo {valor_heuristico_calculado}"
    print(f" [OK] h(n) = {valor_heuristico_calculado} (detectó con precisión que V2 es inalcanzable).")


def test_demostracion_admisibilidad():
    print("\n--- 2. Validando propiedad de Admisibilidad: h(n) <= h*(n) ---")
    diccionario_de_victimas = {
        "V1": VictimaEnRiesgo("V1", 1, 4, ticks_supervivencia=5),
        "V2": VictimaEnRiesgo("V2", 5, 5, ticks_supervivencia=2),
        "V3": VictimaEnRiesgo("V3", 1, 2, ticks_supervivencia=1)
    }

    estado_de_prueba = EstadoDelAgente(1, 1, conjunto_de_victimas_vivas=frozenset(["V1", "V2", "V3"]), tick_actual=0)
    
    valor_heuristico_calculado = calcular_heuristica_de_victimas_condenadas(estado_de_prueba, diccionario_de_victimas)
    cantidad_minima_de_muertes_reales = 1
    
    assert valor_heuristico_calculado <= cantidad_minima_de_muertes_reales, "La heurística sobreestimó el costo real"
    print(f" [OK] h(n) = {valor_heuristico_calculado} <= h*(n) ({cantidad_minima_de_muertes_reales}). Admisibilidad verificada.")


def test_heuristica_compuesta():
    print("\n--- 3. Probando heurística compuesta (pérdidas + distancia más cercana) ---")
    diccionario_de_victimas = {
        "V1": VictimaEnRiesgo("V1", 1, 4, ticks_supervivencia=5),
        "V2": VictimaEnRiesgo("V2", 1, 2, ticks_supervivencia=3)
    }
    estado_de_prueba = EstadoDelAgente(1, 1, conjunto_de_victimas_vivas=frozenset(["V1", "V2"]), tick_actual=0)
    
    perdidas_estimadas, distancia_minima_calculada = calcular_heuristica_para_busqueda_a_estrella(estado_de_prueba, diccionario_de_victimas)
    assert perdidas_estimadas == 0, "No debería haber pérdidas condenadas aún"
    assert distancia_minima_calculada == 1, f"La distancia a la víctima alcanzable más cercana debe ser 1, se obtuvo {distancia_minima_calculada}"
    print(f" [OK] Heurística compuesta: pérdidas={perdidas_estimadas}, dist_minima={distancia_minima_calculada}")


if __name__ == "__main__":
    test_heuristica_victimas_condenadas()
    test_demostracion_admisibilidad()
    test_heuristica_compuesta()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 3.1 PASARON CON ÉXITO! <<<")
