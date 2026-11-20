"""
Pruebas de validación para el diseño y admisibilidad de la Heurística (Tarjeta 3.1).
"""

# Clases del modelo usadas en las pruebas.
from src.models import Estado, Victima
# Las dos heurísticas que se prueban.
from src.heuristics import heuristica_victimas_condenadas, heuristica_a_estrella

# Prueba 1: cálculo del número de víctimas condenadas.
def test_heuristica_victimas_condenadas():
    # Mensaje informativo.
    print("--- 1. Probando cálculo de víctimas condenadas h(n) ---")
    # Posición inicial del agente.
    pos_inicial = (1, 1)
    
    # V1 en (1, 4): distancia = 3. Ticks = 5. (Alcanzable, NO condenada en tick 0)
    # V2 en (5, 5): distancia = |1-5| + |1-5| = 8. Ticks = 2. (Condenada en tick 0: 8 > 2)
    # Diccionario con las dos víctimas de la prueba.
    dict_victimas = {
        "V1": Victima("V1", 1, 4, ticks_supervivencia=5),
        "V2": Victima("V2", 5, 5, ticks_supervivencia=2)
    }

    # Estado en la posición inicial con ambas víctimas vivas, tick 0.
    estado = Estado(
        # Fila del agente.
        fila=pos_inicial[0],
        # Columna del agente.
        columna=pos_inicial[1],
        # Ambas vivas.
        victimas_vivas=frozenset(["V1", "V2"]),
        # Tick 0.
        tick_actual=0
    )

    # Calcula h(n) para ese estado.
    h_val = heuristica_victimas_condenadas(estado, dict_victimas)
    # Debe ser 1: solo V2 está condenada.
    assert h_val == 1, f"Se esperaba 1 víctima condenada (V2), pero se obtuvo {h_val}"
    # Mensaje de éxito.
    print(f" [OK] h(n) = {h_val} (detectó con precisión que V2 es inalcanzable).")


# Prueba 2: comprobación de que h(n) no sobreestima (admisibilidad), en un caso concreto.
def test_demostracion_admisibilidad():
    # Mensaje informativo.
    print("\n--- 2. Validando propiedad de Admisibilidad: h(n) <= h*(n) ---")
    # Tres víctimas de prueba.
    dict_victimas = {
        "V1": Victima("V1", 1, 4, ticks_supervivencia=5),
        "V2": Victima("V2", 5, 5, ticks_supervivencia=2),
        "V3": Victima("V3", 1, 2, ticks_supervivencia=1)
    }

    # Estado en (1, 1), tick 0.
    # Distancia a V1: 3 <= 5 (Viva alcanzable)
    # Distancia a V2: 8 > 2 (Condenada matemáticamente) -> h(n) cuenta 1
    # Distancia a V3: 1 <= 1 (Alcanzable si va primero, pero si va a V1 primero V3 muere)
    # Muertes reales posibles h*(n) >= 1 (como mínimo morirá V2).
    # Estado con las tres víctimas vivas.
    estado = Estado(1, 1, victimas_vivas=frozenset(["V1", "V2", "V3"]), tick_actual=0)
    
    # Valor de la heurística en ese estado.
    h_calculado = heuristica_victimas_condenadas(estado, dict_victimas)
    # El costo real de muertes nunca puede ser menor que las muertes que ya son imposibles de evitar
    # Mínimo de muertes inevitables: 1 (V2), escrito a mano en la prueba.
    muertes_reales_minimas = 1  # V2 es físicamente inalcanzable
    
    # Verifica h(n) <= h*(n): la heurística no sobreestima.
    assert h_calculado <= muertes_reales_minimas, "La heurística sobreestimó el costo real"
    # Mensaje de éxito.
    print(f" [OK] h(n) = {h_calculado} <= h*(n) ({muertes_reales_minimas}). Admisibilidad verificada.")


# Prueba 3: heurística compuesta (pérdidas, distancia a la alcanzable más cercana).
def test_heuristica_compuesta():
    # Mensaje informativo.
    print("\n--- 3. Probando heurística compuesta (pérdidas + distancia más cercana) ---")
    # Dos víctimas, ambas alcanzables.
    dict_victimas = {
        "V1": Victima("V1", 1, 4, ticks_supervivencia=5),
        "V2": Victima("V2", 1, 2, ticks_supervivencia=3)
    }
    # Agente en (1, 1): V2 está a distancia 1, V1 está a distancia 3
    # Estado con ambas vivas en tick 0.
    estado = Estado(1, 1, victimas_vivas=frozenset(["V1", "V2"]), tick_actual=0)
    
    # Calcula la pareja (pérdidas, distancia mínima).
    perdidas, dist_minima = heuristica_a_estrella(estado, dict_victimas)
    # No debe haber pérdidas: ambas son alcanzables.
    assert perdidas == 0, "No debería haber pérdidas condenadas aún"
    # La víctima alcanzable más cercana (V2) está a distancia 1.
    assert dist_minima == 1, f"La distancia a la víctima alcanzable más cercana debe ser 1, se obtuvo {dist_minima}"
    # Mensaje de éxito.
    print(f" [OK] Heurística compuesta: pérdidas={perdidas}, dist_minima={dist_minima}")


# Ejecución directa del archivo.
if __name__ == "__main__":
    # Prueba 1.
    test_heuristica_victimas_condenadas()
    # Prueba 2.
    test_demostracion_admisibilidad()
    # Prueba 3.
    test_heuristica_compuesta()
    # Mensaje final.
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 3.1 PASARON CON ÉXITO! <<<")