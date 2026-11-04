"""
Pruebas de validación para el diseño y admisibilidad de la Heurística (Tarjeta 3.1).
"""

from src.models import Estado, Victima
from src.heuristics import heuristica_victimas_condenadas, heuristica_a_estrella

def test_heuristica_victimas_condenadas():
    print("--- 1. Probando cálculo de víctimas condenadas h(n) ---")
    pos_inicial = (1, 1)
    
    # V1 en (1, 4): distancia = 3. Ticks = 5. (Alcanzable, NO condenada en tick 0)
    # V2 en (5, 5): distancia = |1-5| + |1-5| = 8. Ticks = 2. (Condenada en tick 0: 8 > 2)
    dict_victimas = {
        "V1": Victima("V1", 1, 4, ticks_supervivencia=5),
        "V2": Victima("V2", 5, 5, ticks_supervivencia=2)
    }

    estado = Estado(
        fila=pos_inicial[0],
        columna=pos_inicial[1],
        victimas_vivas=frozenset(["V1", "V2"]),
        tick_actual=0
    )

    h_val = heuristica_victimas_condenadas(estado, dict_victimas)
    assert h_val == 1, f"Se esperaba 1 víctima condenada (V2), pero se obtuvo {h_val}"
    print(f" [OK] h(n) = {h_val} (detectó con precisión que V2 es inalcanzable).")


def test_demostracion_admisibilidad():
    print("\n--- 2. Validando propiedad de Admisibilidad: h(n) <= h*(n) ---")
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
    estado = Estado(1, 1, victimas_vivas=frozenset(["V1", "V2", "V3"]), tick_actual=0)
    
    h_calculado = heuristica_victimas_condenadas(estado, dict_victimas)
    # El costo real de muertes nunca puede ser menor que las muertes que ya son imposibles de evitar
    muertes_reales_minimas = 1  # V2 es físicamente inalcanzable
    
    assert h_calculado <= muertes_reales_minimas, "La heurística sobreestimó el costo real"
    print(f" [OK] h(n) = {h_calculado} <= h*(n) ({muertes_reales_minimas}). Admisibilidad verificada.")


def test_heuristica_compuesta():
    print("\n--- 3. Probando heurística compuesta (pérdidas + distancia más cercana) ---")
    dict_victimas = {
        "V1": Victima("V1", 1, 4, ticks_supervivencia=5),
        "V2": Victima("V2", 1, 2, ticks_supervivencia=3)
    }
    # Agente en (1, 1): V2 está a distancia 1, V1 está a distancia 3
    estado = Estado(1, 1, victimas_vivas=frozenset(["V1", "V2"]), tick_actual=0)
    
    perdidas, dist_minima = heuristica_a_estrella(estado, dict_victimas)
    assert perdidas == 0, "No debería haber pérdidas condenadas aún"
    assert dist_minima == 1, f"La distancia a la víctima alcanzable más cercana debe ser 1, se obtuvo {dist_minima}"
    print(f" [OK] Heurística compuesta: pérdidas={perdidas}, dist_minima={dist_minima}")


if __name__ == "__main__":
    test_heuristica_victimas_condenadas()
    test_demostracion_admisibilidad()
    test_heuristica_compuesta()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 3.1 PASARON CON ÉXITO! <<<")

