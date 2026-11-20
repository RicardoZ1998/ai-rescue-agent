# Agente de Rescate con Víctimas en Riesgo

**Proyecto 1 · Grupo 51 · Introducción a la Inteligencia Artificial**

Integrantes: *(completar)*

## 1. Introducción

Este informe documenta la solución al problema del agente de rescate: una zona de desastre representada como una cuadrícula 2D, donde un agente debe llegar a la celda de cada víctima antes de que se agote su tiempo de supervivencia. Cada movimiento cuesta exactamente 1 tick, el agente no puede esperar y no puede atravesar paredes. Como los tiempos son cortos, normalmente no es posible salvar a todos, así que el objetivo es **maximizar el número de víctimas rescatadas** y, a igualdad de rescatadas, **minimizar los ticks usados**.

Se implementaron desde cero, en Python y sin bibliotecas externas, cuatro estrategias de búsqueda: Amplitud (BFS), Costo Uniforme (UCS), Profundidad Iterativa (IDDFS) y A\*. La interfaz gráfica está hecha con Tkinter y anima la ruta tick a tick.

## 2. Datos de entrada

Mapa (`mapa.txt`, 7 filas × 10 columnas, 29 celdas libres incluida la `S`):

```
##########
#S...#...#
#.##.#.#.#
#....#.#.#
#.##...#.#
#....#...#
##########
```

Víctimas (`victimas.txt`), con el agente iniciando en (1, 1) en el tick 0:

| Id | Posición (fila, col) | Ticks de supervivencia | Distancia Manhattan desde S | Observación |
| --- | --- | --- | --- | --- |
| V1 | (1, 4) | 5 | 3 | Alcanzable |
| V2 | (3, 7) | 12 | 8 | La celda es un muro (`#`): inalcanzable en la práctica |
| V3 | (5, 2) | 3 | 5 | Condenada desde el inicio (5 > 3) |
| V4 | (2, 8) | 20 | 8 | Alcanzable |
| V5 | (4, 5) | 7 | 7 | Alcanzable, con margen justo |

Dos hechos de los datos condicionan todo el análisis posterior. V3 está condenada desde el tick 0 porque ni en línea recta alcanza a llegar. V2 está definida sobre una celda con pared, por lo que ninguna ruta válida puede pisarla (el cargador solo imprime una advertencia y no rechaza el archivo). Por tanto, **el máximo teórico de rescates en este mapa es 3** (V1, V4 y V5).

## 3. Representación del estado

Se siguió la definición formal del enunciado:

> Estado = (fila, columna, conjunto de víctimas vivas, tick actual)

La clase `Estado` añade además el conjunto de víctimas rescatadas, el estado padre y la acción que llevó al estado:

| Atributo | Tipo | Función |
| --- | --- | --- |
| `fila`, `columna` | int | Posición del agente |
| `victimas_vivas` | frozenset de ids | Víctimas que no han muerto ni han sido rescatadas |
| `victimas_rescatadas` | frozenset de ids | Víctimas salvadas hasta este estado |
| `tick_actual` | int | Movimientos realizados (también es el costo acumulado g) |
| `padre`, `accion` | Estado, str | Permiten reconstruir la ruta (N, S, E, O) |

**Por qué esta representación.** Las víctimas fallecidas no se guardan: son las que no están ni vivas ni rescatadas, de modo que `fallecidas = totales − rescatadas − vivas`. Se usan `frozenset` porque son inmutables y hasheables.

**Hash e igualdad.** `__hash__` y `__eq__` se definen sobre la tupla (fila, columna, vivas, rescatadas, tick). El padre y la acción no entran en la identidad, porque dos caminos distintos que llegan al mismo estado deben contar como el mismo estado. Esto hace al estado compatible con conjuntos de visitados, diccionarios de costos y colas de prioridad.

**Función sucesora.** Para cada una de las 4 acciones se calcula la celda destino; si es pared o está fuera del mapa se descarta. Si es válida, el tick sube en 1 y, para cada víctima viva:

1. Si el agente pisa su celda y `nuevo_tick <= ticks_supervivencia`, pasa a rescatadas.
2. Si no la pisa y `nuevo_tick <= ticks_supervivencia`, sigue viva.
3. En cualquier otro caso muere (queda fuera de ambos conjuntos).

**Estado inicial:** agente en `S`, todas las víctimas vivas, tick 0, ninguna rescatada.

**Criterio de parada (estado objetivo).** Un estado es terminal si no quedan víctimas vivas, o si las que quedan no son alcanzables ni siquiera en línea recta (distancia Manhattan mayor que los ticks restantes). Entre los estados terminales se elige el mejor: más rescatadas y, en empate, menos ticks.

## 4. Espacio de búsqueda

- **Factor de ramificación:** como máximo 4 (N, S, E, O); en este mapa, por los pasillos, el factor efectivo es bastante menor (1 a 3 sucesores por estado).
- **Costo de cada acción:** 1 tick, de modo que la profundidad de un nodo coincide con su tick y con su costo g.
- **Profundidad máxima:** acotada por el mayor tiempo de supervivencia (20 ticks en este mapa), porque después de ese tick todas las víctimas están muertas y el estado es terminal.
- **Cota superior del número de estados:** cada víctima puede estar viva, rescatada o muerta (3⁵ = 243 combinaciones), el agente puede estar en 29 celdas y el tick toma valores de 0 a 20 aproximadamente. Eso da del orden de 29 × 243 × 21 ≈ 1,5 × 10⁵ estados como techo teórico. En la práctica son muchos menos los alcanzables (BFS solo expande 509 nodos), porque las víctimas condenadas dejan de importar y las ramas terminales no se expanden.
- **Finitud:** al incluir el tick en el estado el grafo no tiene ciclos reales (todo movimiento avanza el tiempo), y la búsqueda termina cuando todos los estados quedan terminales.

## 5. Algoritmos implementados

Los cuatro comparten la misma función sucesora, el mismo criterio de parada y el mismo criterio de comparación de soluciones (`es_mejor_solucion`). Como no existe un único estado meta, ninguno se detiene en el primer estado terminal: cada uno guarda la **mejor solución terminal** encontrada y solo se detiene antes si logra rescatar a todas las víctimas.

| Algoritmo | Estructura | Control de repetidos | Notas |
| --- | --- | --- | --- |
| BFS | Cola FIFO (`deque`) | Conjunto global de visitados | Explora por niveles de tick |
| UCS | Min-heap (`heapq`) con (g, contador, estado) | Diccionario de mejor costo g por estado | Como todos los pasos cuestan 1, g = tick y se comporta igual que BFS |
| IDDFS | Recursión con límite creciente (0, 1, 2, …) | Solo la ruta activa (evita ciclos en la rama), sin visitados global | Cota = min(cota pedida, máx. ticks de víctimas + 5); la GUI usa cota 16 |
| A\* | Min-heap con (pérdidas, distancia, g, contador, estado) | Diccionario de mejor g y poda por cota | Usa heurística y poda |

El contador secuencial del heap sirve de desempate para que Python nunca tenga que comparar dos objetos `Estado` entre sí.

Los **nodos expandidos** se cuentan cada vez que un nodo sale de la frontera (o se visita, en IDDFS), incluidos los terminales.

## 6. Heurísticas

### 6.1 Heurística base del enunciado

`h(n)` = número de víctimas vivas condenadas, donde una víctima es condenada si `distancia_Manhattan(agente, v) > ticks_restantes(v)` (con `ticks_restantes = ticks_supervivencia − tick_actual`).

### 6.2 Heurística implementada en A\* (más informada)

Se devuelve una pareja `(pérdidas estimadas, distancia mínima)`:

1. **Pérdidas estimadas** = víctimas que ya murieron + víctimas vivas condenadas. Las ya muertas se obtienen como `totales − rescatadas − vivas`.
2. **Distancia mínima** = distancia Manhattan a la víctima alcanzable más cercana. Solo se usa para ordenar la frontera y empujar al agente hacia el siguiente rescate; no interviene en la poda.

La cola de prioridad compara las tuplas de forma lexicográfica: primero pérdidas, luego distancia, luego g. Es decir, no es la suma clásica g + h, sino una ordenación por la cantidad de pérdidas que ya son inevitables.

### 6.3 Demostración de admisibilidad

El objetivo a minimizar es el número de víctimas perdidas. Sea `h*(n)` el mínimo de muertes adicionales (entre las víctimas hoy vivas) sobre todas las continuaciones posibles desde `n`. Se debe probar que `h(n) ≤ h*(n)`.

1. Sea `v` una víctima viva y condenada en `n`: `d_M(agente, v) > r`, con `r` sus ticks restantes.
2. La distancia real mínima por celdas libres cumple `d_real ≥ d_M`, porque las paredes solo pueden alargar el camino, nunca acortarlo.
3. Cada movimiento consume exactamente 1 tick y el agente no puede esperar. Entonces, cualquier camino hacia `v` llega en el tick `t + d_real ≥ t + d_M > t + r`, que es posterior a su límite.
4. Por tanto `v` muere en **toda** continuación posible. Cada víctima condenada aporta al menos 1 a `h*(n)`.
5. Las víctimas condenadas son distintas entre sí, así que `h*(n) ≥ (número de condenadas) = h(n)`. ∎

Para la versión compuesta, las víctimas que ya murieron son pérdidas ya consumadas y se suman exactamente, por lo que `perdidas_f(n) = muertas(n) + h(n)` sigue siendo una cota inferior de las pérdidas de cualquier estado terminal descendiente de `n`.

**Monotonía.** Tras un movimiento, `r' = r − 1` y `d_M' ≥ d_M − 1`; si `d_M > r` entonces `d_M' ≥ d_M − 1 > r − 1 = r'`. Una víctima condenada sigue condenada, o muere y pasa al término de las ya muertas. Por eso `perdidas_f` nunca disminuye a lo largo de un camino.

**Consecuencia para la poda.** Un nodo con `perdidas_f` mayor que las pérdidas de la mejor solución ya hallada no puede mejorarla y se descarta. Un nodo con las mismas pérdidas pero con `g` mayor o igual a los ticks de la mejor solución tampoco puede mejorarla, porque los ticks solo crecen. Ambas podas son seguras gracias a la admisibilidad, así que A\* conserva la optimalidad.

### 6.4 Limitaciones de la heurística

- Ignora las paredes: usa Manhattan, que subestima la distancia real. Una versión más informada usaría la distancia real por BFS sobre el mapa (precalculada una vez).
- No detecta que V2 está sobre un muro; solo la descartaría cuando se agote su tiempo.
- No considera el costo de visitar varias víctimas en secuencia (es un problema tipo viajante); solo mira víctimas por separado.

## 7. Interfaz gráfica (Tkinter)

La aplicación (`AppRescate`) tiene dos columnas:

- **Controles:** carga de `mapa.txt` y `victimas.txt` con botón "Examinar", ruta del archivo e indicador verde o rojo de lectura correcta; menú desplegable de algoritmo (A\*, BFS, UCS, IDDFS); deslizador de velocidad de 50 a 1000 ms por tick; botones Iniciar Rescate, Pausar/Reanudar, Reiniciar y Comparar los 4 algoritmos; panel con dimensiones, inicio y total de víctimas.
- **Visualización:** lienzo (`Canvas`) que se redibuja en cada tick con el agente en azul, las víctimas vivas en naranja con su contador de ticks restantes, las rescatadas en verde y las fallecidas en rojo, más una leyenda de colores.
- **Estadísticas:** caja con víctimas totales, rescatadas, fallecidas, ticks, nodos y tiempo del algoritmo ejecutado, y una tabla comparativa (Algoritmo, Nodos, Tiempo, Rescatadas, Fallecidas, Ticks).

La animación recorre la lista de pasos del resultado y se reprograma con `after`, usando la velocidad elegida. Los errores de carga (archivo inexistente, filas de distinto largo, mapa sin `S` o con más de una, datos no numéricos) se muestran en cuadros de error.

## 8. Pruebas y resultados

### 8.1 Pruebas automáticas

| Archivo | Qué verifica |
| --- | --- |
| `test_estado.py` | Estado hasheable y usable en `set`; sucesores respetan paredes y rescatan a tiempo; las víctimas mueren al expirar su tiempo |
| `test_evaluator.py` | Distancia Manhattan, alcanzabilidad, detección de estado objetivo, criterio de mejor solución (más rescatadas y desempate por ticks) |
| `test_heuristics.py` | Conteo de condenadas, comprobación de admisibilidad en un caso, heurística compuesta |
| `test_bfs.py`, `test_ucs.py`, `test_iddfs.py` | Mapa mínimo 3×3 (1 rescate en 1 tick) y mapa del proyecto |
| `test_astar.py` | Mapa mínimo; en el mapa oficial exige 3 rescatadas en 14 ticks; compara los 4 algoritmos y exige que A\* expanda menos nodos que BFS |
| `test_gui.py` | Creación de la ventana y de sus widgets principales (requiere un entorno con Tkinter y pantalla) |

Se ejecutan desde la raíz del proyecto, por ejemplo `python -m tests.test_astar`.

### 8.2 Comparación de los 4 algoritmos (mapa oficial)

| Algoritmo | Nodos expandidos | Tiempo | Rescatadas | Fallecidas | Ticks |
| --- | --- | --- | --- | --- | --- |
| BFS | 509 | ≈ 2,4 ms | 3 | 2 | 14 |
| UCS | 509 | ≈ 2,1 ms | 3 | 2 | 14 |
| IDDFS (cota 16) | 541.204 | ≈ 1,34 s | 3 | 2 | 14 |
| A\* | 99 | ≈ 0,7 ms | 3 | 2 | 14 |

Los tiempos son de una ejecución y dependen del equipo; los nodos son deterministas.

### 8.3 Ruta encontrada (idéntica en los cuatro algoritmos)

E, E, E, S, S, S, E, E, N, N, N, E, E, S (14 movimientos):

| Tick | Celda | Evento |
| --- | --- | --- |
| 0 | (1, 1) | Inicio |
| 3 | (1, 4) | Rescata V1 (límite 5) |
| 7 | (4, 5) | Rescata V5 (límite 7, justo a tiempo) |
| 14 | (2, 8) | Rescata V4 (límite 20) |

### 8.4 Traza de A\* (primeras 8 expansiones)

La prioridad es (pérdidas, distancia, g). El estado inicial tiene h = (1, 3): una pérdida estimada (V3) y distancia 3 a la víctima alcanzable más cercana (V1). "Hijos creados" son los sucesores que entraron a la frontera.

| Paso | Expande (celda, tick, prioridad) | Hijos creados (celda, pérdidas, dist.) | Frontera después |
| --- | --- | --- | --- |
| 1 | (1,1), t0, (1,3,0) | (2,1) → (1,4); (1,2) → (1,2) | 2 nodos |
| 2 | (1,2), t1, (1,2,1) | (1,3) → (1,1); (1,1) → (2,3) | 3 nodos |
| 3 | (1,3), t2, (1,1,2) | (1,4) → (1,4); (1,2) → (2,2) | 4 nodos |
| 4 | (2,1), t1, (1,4,1) | (3,1) → (2,5) | 4 nodos |
| 5 | (1,4), t3, (1,4,3) | (2,4) → (1,3); (1,3) → (2,6) | 5 nodos |
| 6 | (2,4), t4, (1,3,4) | (1,4) → (2,5); (3,4) → (1,2) | 6 nodos |
| 7 | (3,4), t5, (1,2,5) | (2,4) → (2,4); (4,4) → (1,1); (3,3) → (2,4) | 8 nodos |
| 8 | (4,4), t6, (1,1,6) | (3,4) → (2,3); (5,4) → (2,5); (4,5) → (1,3) | 10 nodos |

Se observa cómo la frontera da prioridad a los nodos que conservan solo la pérdida inevitable (V3) y se acercan a una víctima alcanzable, y cómo los retrocesos suben a 2 pérdidas estimadas porque dejan a otra víctima fuera de alcance.

## 9. Análisis

**Optimalidad.** Los cuatro algoritmos obtienen el mismo resultado: 3 rescatadas en 14 ticks. Como V2 (muro) y V3 (condenada) no pueden salvarse, 3 es el máximo posible, de modo que la solución es óptima en víctimas. Los tres algoritmos exhaustivos (BFS, UCS, IDDFS) y A\* coinciden también en los ticks.

**BFS y UCS.** Expanden exactamente los mismos nodos (509). Con costo unitario por acción, el costo g equivale al nivel de profundidad, así que UCS degenera en BFS; la diferencia es solo la estructura (cola FIFO frente a heap).

**IDDFS.** Es el más costoso por mucho: 541.204 nodos, unas 1.000 veces más que BFS. Tiene memoria muy baja (solo guarda la rama actual), pero al no mantener un conjunto de visitados global vuelve a explorar los mismos estados por distintos caminos y además repite las iteraciones previas en cada nuevo límite. En un espacio donde muchos caminos llevan al mismo estado, eso se paga caro.

**A\*.** Expande 99 nodos, unas 5 veces menos que BFS y UCS, y es el más rápido. La ganancia proviene de dos fuentes: la heurística ordena la frontera hacia ramas con menos pérdidas inevitables y la poda por cota descarta ramas que ya no pueden superar la mejor solución. Como la heurística es admisible y monótona, no se pierde optimalidad.

**Complejidad.** En el peor caso BFS, UCS y A\* son O(b^d) en tiempo y memoria sobre el espacio de estados (acotado aquí por ≈ 1,5 × 10⁵); IDDFS es O(b^d) en tiempo con memoria O(d), pero con una constante mucho mayor por las repeticiones.

## 10. Limitaciones y trabajo futuro

- **Restricción blanda de víctimas críticas:** no se implementó (los datos no incluyen un campo de criticidad).
- **Cota de IDDFS en la GUI:** se fija en 16 ticks por rendimiento; en un mapa con rutas óptimas más largas podría no hallar la mejor solución. El valor por defecto de la función es 50 (limitado a máx. ticks + 5).
- **Heurística:** puede mejorarse usando distancias reales por BFS en lugar de Manhattan, y considerando el orden de visita de varias víctimas.
- **Validación de datos:** una víctima sobre un muro solo genera una advertencia en consola; podría rechazarse o mostrarse en la GUI.
- **Interfaz:** los algoritmos corren en el hilo principal de Tkinter, por lo que mapas muy grandes congelarían la ventana mientras se calcula.

## 11. Conclusiones

Se modeló el problema con un estado explícito, inmutable y hasheable que incluye la posición, las víctimas vivas y rescatadas y el tick, y se resolvió con cuatro estrategias que comparten una misma función sucesora y un mismo criterio de optimalidad (más rescatadas, luego menos ticks). En el mapa oficial todos encuentran la solución óptima (3 de 5 víctimas en 14 ticks), pero con costos muy distintos: A\* con una heurística admisible reduce los nodos expandidos de 509 a 99 respecto a BFS y UCS, y IDDFS llega a más de 541 mil por no recordar estados ya visitados.

## Anexo: estructura del proyecto

```
main.py                    Punto de entrada
data/mapa.txt, victimas.txt
src/models.py              Victima, Mapa, Estado (sucesores, ruta)
src/loader.py              Carga y validación de archivos
src/evaluator.py           Manhattan, alcanzabilidad, objetivo, mejor solución
src/heuristics.py          Heurística base y compuesta
src/algorithms/            bfs.py, ucs.py, iddfs.py, astar.py
src/gui/app.py             Interfaz Tkinter
tests/                     Pruebas por módulo
```
