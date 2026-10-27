"""
Pruebas de validación para el Criterio de Estado Objetivo y Evaluación (Tarjeta 1.3).
"""

from src.models import Estado, Victima
from src.evaluator import (
    distancia_manhattan,
    es_victima_alcanzable,
    es_estado_objetivo,
    es_mejor_solucion
)

def test_distancia_y_alcanzabilidad():
    print("--- 1. Probando distancia Manhattan y alcanzabilidad ---")
    pos_agente = (1, 1)
    
    # Víctima V1 en (1, 4): distancia Manhattan = |1-1| + |1-4| = 3
    assert distancia_manhattan(pos_agente, (1, 4)) == 3
    
    # Caso alcanzable: distancia es 3 y tiene 5 ticks de vida (alcanzable en tick 0)
    v1 = Victima("V1", 1, 4, ticks_supervivencia=5)
    assert es_victima_alcanzable(pos_agente, tick_actual=0, victima=v1) == True
    
    # Caso inalcanzable: distancia es 3 pero en tick 3 solo le quedan 5 - 3 = 2 ticks restantes
    # distancia(3) > ticks_restantes(2) -> Inalcanzable
    assert es_victima_alcanzable(pos_agente, tick_actual=3, victima=v1) == False
    print(" [OK] Distancia Manhattan y alcanzabilidad funcionan según las reglas temporales.")


def test_es_estado_objetivo():
    print("\n--- 2. Probando detección de Estado Objetivo ---")
    dict_victimas = {
        "V1": Victima("V1", 1, 4, ticks_supervivencia=5),
        "V2": Victima("V2", 5, 5, ticks_supervivencia=2)
    }

    # Caso A: No quedan víctimas vivas (todas rescatadas o muertas) -> ES OBJETIVO
    estado_vacio = Estado(1, 1, victimas_vivas=frozenset(), tick_actual=4)
    assert es_estado_objetivo(estado_vacio, dict_victimas) == True

    # Caso B: Queda V1 viva y es alcanzable desde (1, 1) en tick 0 -> NO ES OBJETIVO
    estado_con_esperanza = Estado(1, 1, victimas_vivas=frozenset(["V1"]), tick_actual=0)
    assert es_estado_objetivo(estado_con_esperanza, dict_victimas) == False

    # Caso C: Queda V2 viva en (5, 5) con 2 ticks de vida, agente en (1, 1) en tick 0
    # Distancia = |1-5| + |1-5| = 8. Ticks restantes = 2. Es imposible llegar -> ES OBJETIVO
    estado_sin_esperanza = Estado(1, 1, victimas_vivas=frozenset(["V2"]), tick_actual=0)
    assert es_estado_objetivo(estado_sin_esperanza, dict_victimas) == True
    print(" [OK] Estado objetivo detecta correctamente cuando no hay víctimas alcanzables.")


def test_comparacion_soluciones():
    print("\n--- 3. Probando criterios de desempate y mejor solución ---")
    # Solución A: 2 rescatadas en 10 ticks
    sol_a = Estado(1, 1, frozenset(), tick_actual=10, victimas_rescatadas=frozenset(["V1", "V2"]))
    # Solución B: 3 rescatadas en 15 ticks
    sol_b = Estado(1, 1, frozenset(), tick_actual=15, victimas_rescatadas=frozenset(["V1", "V2", "V3"]))
    # Solución C: 2 rescatadas en 8 ticks
    sol_c = Estado(1, 1, frozenset(), tick_actual=8, victimas_rescatadas=frozenset(["V1", "V2"]))

    # B debe ser mejor que A porque rescató más víctimas (3 > 2), aunque tomó más ticks
    assert es_mejor_solucion(candidato=sol_b, actual_mejor=sol_a) == True
    assert es_mejor_solucion(candidato=sol_a, actual_mejor=sol_b) == False

    # C debe ser mejor que A porque rescataron la misma cantidad (2), pero C fue más rápida (8 ticks < 10 ticks)
    assert es_mejor_solucion(candidato=sol_c, actual_mejor=sol_a) == True
    assert es_mejor_solucion(candidato=sol_a, actual_mejor=sol_c) == False
    print(" [OK] Criterio principal (más víctimas) y desempate (menos ticks) validados.")


if __name__ == "__main__":
    test_distancia_y_alcanzabilidad()
    test_es_estado_objetivo()
    test_comparacion_soluciones()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 1.3 PASARON CON ÉXITO! <<<")
