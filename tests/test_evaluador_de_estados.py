from src.modelos_de_datos import EstadoDelAgente, VictimaEnRiesgo
from src.evaluador_de_estados import (
    calcular_distancia_manhattan,
    es_victima_alcanzable,
    es_estado_objetivo,
    es_mejor_solucion
)

def test_distancia_y_alcanzabilidad():
    print("--- 1. Probando distancia Manhattan y alcanzabilidad ---")
    posicion_del_agente_de_prueba = (1, 1)
    
    assert calcular_distancia_manhattan(posicion_del_agente_de_prueba, (1, 4)) == 3
    
    victima_de_prueba = VictimaEnRiesgo("V1", 1, 4, ticks_supervivencia=5)
    assert es_victima_alcanzable(posicion_del_agente_de_prueba, tick_actual=0, victima=victima_de_prueba) == True
    assert es_victima_alcanzable(posicion_del_agente_de_prueba, tick_actual=3, victima=victima_de_prueba) == False
    print(" [OK] Distancia Manhattan y alcanzabilidad funcionan según las reglas temporales.")


def test_es_estado_objetivo():
    print("\n--- 2. Probando detección de Estado Objetivo ---")
    diccionario_de_victimas = {
        "V1": VictimaEnRiesgo("V1", 1, 4, ticks_supervivencia=5),
        "V2": VictimaEnRiesgo("V2", 5, 5, ticks_supervivencia=2)
    }

    estado_sin_victimas_vivas = EstadoDelAgente(1, 1, conjunto_de_victimas_vivas=frozenset(), tick_actual=4)
    assert es_estado_objetivo(estado_sin_victimas_vivas, diccionario_de_victimas) == True

    estado_con_victima_alcanzable = EstadoDelAgente(1, 1, conjunto_de_victimas_vivas=frozenset(["V1"]), tick_actual=0)
    assert es_estado_objetivo(estado_con_victima_alcanzable, diccionario_de_victimas) == False

    estado_con_victima_inalcanzable = EstadoDelAgente(1, 1, conjunto_de_victimas_vivas=frozenset(["V2"]), tick_actual=0)
    assert es_estado_objetivo(estado_con_victima_inalcanzable, diccionario_de_victimas) == True
    print(" [OK] Estado objetivo detecta correctamente cuando no hay víctimas alcanzables.")


def test_comparacion_soluciones():
    print("\n--- 3. Probando criterios de desempate y mejor solución ---")
    solucion_con_dos_rescatadas_y_diez_ticks = EstadoDelAgente(1, 1, frozenset(), tick_actual=10, conjunto_de_victimas_rescatadas=frozenset(["V1", "V2"]))
    solucion_con_tres_rescatadas_y_quince_ticks = EstadoDelAgente(1, 1, frozenset(), tick_actual=15, conjunto_de_victimas_rescatadas=frozenset(["V1", "V2", "V3"]))
    solucion_con_dos_rescatadas_y_ocho_ticks = EstadoDelAgente(1, 1, frozenset(), tick_actual=8, conjunto_de_victimas_rescatadas=frozenset(["V1", "V2"]))

    assert es_mejor_solucion(estado_candidato=solucion_con_tres_rescatadas_y_quince_ticks, actual_mejor_estado=solucion_con_dos_rescatadas_y_diez_ticks) == True
    assert es_mejor_solucion(estado_candidato=solucion_con_dos_rescatadas_y_diez_ticks, actual_mejor_estado=solucion_con_tres_rescatadas_y_quince_ticks) == False

    assert es_mejor_solucion(estado_candidato=solucion_con_dos_rescatadas_y_ocho_ticks, actual_mejor_estado=solucion_con_dos_rescatadas_y_diez_ticks) == True
    assert es_mejor_solucion(estado_candidato=solucion_con_dos_rescatadas_y_diez_ticks, actual_mejor_estado=solucion_con_dos_rescatadas_y_ocho_ticks) == False
    print(" [OK] Criterio principal (más víctimas) y desempate (menos ticks) validados.")


if __name__ == "__main__":
    test_distancia_y_alcanzabilidad()
    test_es_estado_objetivo()
    test_comparacion_soluciones()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 1.3 PASARON CON ÉXITO! <<<")
