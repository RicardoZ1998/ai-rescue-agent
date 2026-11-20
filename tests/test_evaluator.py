"""
Pruebas de validación para el Criterio de Estado Objetivo y Evaluación (Tarjeta 1.3).
"""

# Clases del modelo usadas en las pruebas.
from src.models import Estado, Victima
# Funciones del evaluador que se van a probar.
from src.evaluator import (
    # Distancia Manhattan.
    distancia_manhattan,
    # ¿Víctima alcanzable?
    es_victima_alcanzable,
    # ¿Estado terminal?
    es_estado_objetivo,
    # ¿Candidato mejor que la mejor solución actual?
    es_mejor_solucion
)

# Prueba 1: distancia Manhattan y alcanzabilidad.
def test_distancia_y_alcanzabilidad():
    # Mensaje informativo.
    print("--- 1. Probando distancia Manhattan y alcanzabilidad ---")
    # Posición del agente para la prueba.
    pos_agente = (1, 1)
    
    # Víctima V1 en (1, 4): distancia Manhattan = |1-1| + |1-4| = 3
    # La distancia de (1,1) a (1,4) debe ser 3.
    assert distancia_manhattan(pos_agente, (1, 4)) == 3
    
    # Caso alcanzable: distancia es 3 y tiene 5 ticks de vida (alcanzable en tick 0)
    # Crea la víctima V1 con 5 ticks de supervivencia.
    v1 = Victima("V1", 1, 4, ticks_supervivencia=5)
    # En tick 0: 3 <= 5 → alcanzable (True).
    assert es_victima_alcanzable(pos_agente, tick_actual=0, victima=v1) == True
    
    # Caso inalcanzable: distancia es 3 pero en tick 3 solo le quedan 5 - 3 = 2 ticks restantes
    # distancia(3) > ticks_restantes(2) -> Inalcanzable
    # En tick 3: 3 > 2 → inalcanzable (False).
    assert es_victima_alcanzable(pos_agente, tick_actual=3, victima=v1) == False
    # Mensaje de éxito.
    print(" [OK] Distancia Manhattan y alcanzabilidad funcionan según las reglas temporales.")


# Prueba 2: detección del estado objetivo (terminal).
def test_es_estado_objetivo():
    # Mensaje informativo.
    print("\n--- 2. Probando detección de Estado Objetivo ---")
    # Dos víctimas de prueba: V1 cercana con tiempo de sobra y V2 lejana con poco tiempo.
    dict_victimas = {
        "V1": Victima("V1", 1, 4, ticks_supervivencia=5),
        "V2": Victima("V2", 5, 5, ticks_supervivencia=2)
    }

    # Caso A: No quedan víctimas vivas (todas rescatadas o muertas) -> ES OBJETIVO
    # Estado sin víctimas vivas.
    estado_vacio = Estado(1, 1, victimas_vivas=frozenset(), tick_actual=4)
    # Debe ser objetivo.
    assert es_estado_objetivo(estado_vacio, dict_victimas) == True

    # Caso B: Queda V1 viva y es alcanzable desde (1, 1) en tick 0 -> NO ES OBJETIVO
    # Estado con V1 viva y alcanzable.
    estado_con_esperanza = Estado(1, 1, victimas_vivas=frozenset(["V1"]), tick_actual=0)
    # No debe ser objetivo todavía.
    assert es_estado_objetivo(estado_con_esperanza, dict_victimas) == False

    # Caso C: Queda V2 viva en (5, 5) con 2 ticks de vida, agente en (1, 1) en tick 0
    # Distancia = |1-5| + |1-5| = 8. Ticks restantes = 2. Es imposible llegar -> ES OBJETIVO
    # Estado con solo V2 viva, pero inalcanzable.
    estado_sin_esperanza = Estado(1, 1, victimas_vivas=frozenset(["V2"]), tick_actual=0)
    # Debe ser objetivo (nada más que rescatar).
    assert es_estado_objetivo(estado_sin_esperanza, dict_victimas) == True
    # Mensaje de éxito.
    print(" [OK] Estado objetivo detecta correctamente cuando no hay víctimas alcanzables.")


# Prueba 3: comparación de soluciones (más rescatadas; desempate por menos ticks).
def test_comparacion_soluciones():
    # Mensaje informativo.
    print("\n--- 3. Probando criterios de desempate y mejor solución ---")
    # Solución A: 2 rescatadas en 10 ticks
    sol_a = Estado(1, 1, frozenset(), tick_actual=10, victimas_rescatadas=frozenset(["V1", "V2"]))
    # Solución B: 3 rescatadas en 15 ticks
    sol_b = Estado(1, 1, frozenset(), tick_actual=15, victimas_rescatadas=frozenset(["V1", "V2", "V3"]))
    # Solución C: 2 rescatadas en 8 ticks
    sol_c = Estado(1, 1, frozenset(), tick_actual=8, victimas_rescatadas=frozenset(["V1", "V2"]))

    # B debe ser mejor que A porque rescató más víctimas (3 > 2), aunque tomó más ticks
    # B es mejor que A.
    assert es_mejor_solucion(candidato=sol_b, actual_mejor=sol_a) == True
    # A NO es mejor que B.
    assert es_mejor_solucion(candidato=sol_a, actual_mejor=sol_b) == False

    # C debe ser mejor que A porque rescataron la misma cantidad (2), pero C fue más rápida (8 ticks < 10 ticks)
    # C es mejor que A por desempate de ticks.
    assert es_mejor_solucion(candidato=sol_c, actual_mejor=sol_a) == True
    # A NO es mejor que C.
    assert es_mejor_solucion(candidato=sol_a, actual_mejor=sol_c) == False
    # Mensaje de éxito.
    print(" [OK] Criterio principal (más víctimas) y desempate (menos ticks) validados.")


# Ejecución directa del archivo.
if __name__ == "__main__":
    # Prueba 1.
    test_distancia_y_alcanzabilidad()
    # Prueba 2.
    test_es_estado_objetivo()
    # Prueba 3.
    test_comparacion_soluciones()
    # Mensaje final.
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 1.3 PASARON CON ÉXITO! <<<")