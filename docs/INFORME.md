# Proyecto 1: Agente de Rescate con Víctimas en Riesgo
## Inteligencia Artificial - Búsqueda en Espacios de Estados con Restricciones Temporales

**Autor:** Ricardo Zuluaga Pulgarin  
**Lenguaje:** Python 3.12 (Implementación nativa sin dependencias externas)  
**Interfaz Gráfica:** Tkinter  

---

## 1. Introducción y Descripción del Problema

El presente proyecto aborda el problema de un **Agente de Rescate en una zona de desastre 2D** modelada como una cuadrícula discreta con celdas transitables (`.`), muros infranqueables (`#`) y una posición de inicio (`S`).

El entorno contiene un conjunto de víctimas $V = \{v_1, v_2, \dots, v_k\}$, donde cada víctima $v_i$ posee:
- Una posición espacial fija en la cuadrícula $(fila_{v_i}, col_{v_i})$.
- Un tiempo límite de supervivencia medido en *ticks* discretos de simulación: $t_{max}(v_i)$.

### Dinámica Temporal y Restricciones Duras:
1. Cada acción de desplazamiento del agente consume exactamente **1 tick** de simulación (costo unitario $c = 1$).
2. El agente se desplaza en las 4 direcciones cardinales (Norte, Sur, Este, Oeste).
3. Una víctima es rescatada automáticamente si el agente pisa su celda en un tick $t \le t_{max}(v_i)$.
4. Si el reloj de la simulación supera los ticks de supervivencia de una víctima antes de que el agente arribe ($t > t_{max}(v_i)$), la víctima fallece de forma irreversible.
5. El agente **no puede esperar** (debe desplazarse obligatoriamente en cada turno).
6. **Objetivo Global:** Dado que el agente solo avanza una celda por tick y los tiempos de supervivencia son limitados, resulta imposible salvar a todas las víctimas en la mayoría de los escenarios. Por ende, el objetivo es **encontrar la ruta que maximice el número de víctimas rescatadas**, desempatando por la ruta de menor duración en ticks.

---

## 2. Definición Formal del Estado y Espacio de Búsqueda

### 2.1 Representación Formal del Estado
El estado del sistema no puede modelarse únicamente mediante las coordenadas espaciales $(x, y)$, ya que el tiempo transcurrido y la supervivencia de las víctimas introducen dinamismo temporal. Por ende, el estado se define formalmente como la 4-tupla:

$$E = (fila, columna, V_{vivas}, V_{rescatadas}, tick_{actual})$$

Donde:
- $(fila, columna) \in \mathbb{N} \times \mathbb{N}$: Coordenadas cartesianas actuales del agente dentro del mapa.
- $V_{vivas} \subseteq V$: Subconjunto inmutable (`frozenset`) de identificadores de víctimas que continúan vivas y no han sido rescatadas aún.
- $V_{rescatadas} \subseteq V$: Subconjunto inmutable (`frozenset`) de identificadores de víctimas ya rescatadas exitosamente hasta este estado.
- $tick_{actual} \in \mathbb{N}_0$: Número acumulado de pasos/ticks transcurridos desde el inicio de la búsqueda ($g(n) = tick_{actual}$).

### 2.2 Justificación de Inmutabilidad y Hashing
Para que las estructuras de búsqueda (conjunto cerrado de visitados `set` y colas de prioridad `heapq`) operen en tiempo constante $O(1)$, los estados deben ser **hasheables e inmutables**:
- Los conjuntos de víctimas se encapsulan en estructuras `frozenset`.
- Los métodos `__hash__` y `__eq__` se implementan considerando la tupla completa:
  $$\text{hash}(E) = \text{hash}((fila, columna, V_{vivas}, V_{rescatadas}, tick_{actual}))$$
- **Importancia teórica:** Si dos ramas alcanzan la misma casilla $(r, c)$ en el mismo $tick$, pero una rescató a una víctima y la otra no, corresponden a estados distintos del problema. Incluir $V_{rescatadas}$ en el hash previene la poda indebida de ramas óptimas.

---

## 3. Función Sucesora y Criterios de Parada

### 3.1 Función de Transición $\text{Sucesores}(E)$
Dado un estado $E$, se evalúan los 4 movimientos ortogonales $\Delta \in \{(-1, 0), (1, 0), (0, 1), (0, -1)\}$:
1. Se calcula la nueva coordenada $(fila', columna') = (fila + \Delta_r, columna + \Delta_c)$.
2. Se verifica que $mapa[fila'][columna'] \neq '\#'$ y esté dentro de las dimensiones del mapa.
3. Se avanza el reloj: $tick' = tick_{actual} + 1$.
4. **Actualización del estado de víctimas:**
   - Para cada $v \in V_{vivas}$:
     - Si $(fila', columna') = (fila_v, col_v)$ y $tick' \le t_{max}(v)$, $v$ se transfiere a $V'_{rescatadas}$.
     - Si el agente no está en su celda pero $tick' \le t_{max}(v)$, $v$ permanece en $V'_{vivas}$.
     - Si $tick' > t_{max}(v)$, la víctima fallece y se descarta de $V'_{vivas}$.

### 3.2 Criterio de Estado Objetivo (Terminal)
Un estado es considerado **Objetivo/Terminal** si no existe ninguna víctima viva alcanzable:
$$\text{es\_objetivo}(E) \iff |V_{vivas}| = 0 \quad \lor \quad \forall v \in V_{vivas}: D_M(agente, v) > (t_{max}(v) - tick_{actual})$$
Donde $D_M$ es la distancia Manhattan. Esta condición permite una **poda temprana fundamental**, evitando que los algoritmos sigan generando estados inútiles cuando ya nadie más puede ser salvado.

---

## 4. Diseño de la Heurística de A* y Demostración de Admisibilidad

### 4.1 Definición Matemática de la Heurística Base
Se adopta la heurística propuesta en el enunciado:
$$h(n) = \text{número de víctimas vivas condenadas a morir desde el estado } n$$

Una víctima $v \in V_{vivas}$ está condenada si:
$$D_M(agente, v) > (t_{max}(v) - tick_{actual})$$

### 4.2 Demostración Formal de Admisibilidad

**Teorema:** La función heurística $h(n)$ es admisible, es decir:
$$h(n) \le h^*(n), \quad \forall n$$
donde $h^*(n)$ representa la cantidad real mínima de víctimas que morirán en el futuro a partir de $n$.

**Demostración:**
1. En una cuadrícula bidimensional con obstáculos, la distancia Manhattan $D_M(A, B) = |\Delta r| + |\Delta c|$ representa la distancia mínima teórica entre dos celdas (longitud del camino geodésico en un grafo libre de muros).
2. Para cualquier camino real que respete los muros (`#`), la distancia real $D_{real}(A, B)$ satisface la cota inferior:
   $$D_{real}(A, B) \ge D_M(A, B)$$
3. El tiempo necesario para que el agente alcance la posición de la víctima $v$ es como mínimo $D_{real}(agente, v)$ ticks.
4. Si la condición de condena se cumple:
   $$D_M(agente, v) > t_{restantes}(v)$$
5. Por transitividad de desigualdades:
   $$D_{real}(agente, v) \ge D_M(agente, v) > t_{restantes}(v) \implies D_{real}(agente, v) > t_{restantes}(v)$$
6. En consecuencia, es físicamente imposible que el agente arribe a la víctima antes de que expire su tiempo de supervivencia. La muerte de $v$ es un hecho matemáticamente ineludible en toda rama sucesora.
7. Dado que $h(n)$ únicamente contabiliza víctimas cuya defunción es $100\%$ segura, y en la realidad podrían morir víctimas adicionales por restricciones de trayectorias concurrentes, se cumple rigurosamente:
   $$h(n) \le h^*(n)$$
   $\blacksquare$ **Q.E.D. (Queda Demostrado)**

---

## 5. Implementación de Algoritmos y Complejidad Teórica

Se implementaron desde cero 4 estrategias de búsqueda:

| Algoritmo | Tipo | Estructura de Datos | Complejidad Temporal | Complejidad Espacial |
| :--- | :--- | :--- | :--- | :--- |
| **BFS** (Amplitud) | No informada | Cola FIFO (`deque`) | $O(b^d)$ | $O(b^d)$ |
| **UCS** (Costo Uniforme) | No informada | Min-Heap (`heapq`) | $O(b^{1 + \lfloor C^* / \epsilon \rfloor})$ | $O(b^{1 + \lfloor C^* / \epsilon \rfloor})$ |
| **IDDFS** (Prof. Iterativa) | No informada | Pila de llamadas (DLS) | $O(b^d)$ | $O(b \cdot d)$ |
| **A\*** | Informada | Min-Heap + Heurística | $O(b^d)$ peor caso / $O(d)$ mejor | $O(b^d)$ |

---

## 6. Resultados Experimentales y Análisis Comparativo

### 6.1 Resultados sobre el Mapa Oficial del Proyecto (`data/mapa.txt`)

Se ejecutaron los cuatro algoritmos sobre el mapa oficial proporcionado en el enunciado (cuadrícula $7 \times 10$, 5 víctimas).

```text
========================================================================================
                      RESULTADOS COMPARATIVOS EXPERIMENTALES
========================================================================================
Algoritmo    | Nodos Expandidos | Tiempo (seg) | Rescatadas | Fallecidas | Ticks Totales
----------------------------------------------------------------------------------------
BFS          | 509              | 0.0017s      | 3          | 2          | 14
UCS          | 509              | 0.0020s      | 3          | 2          | 14
IDDFS        | 541,204          | 1.1073s      | 3          | 2          | 14
A*           | 99               | 0.0007s      | 3          | 2          | 14
========================================================================================
```

### 6.2 Secuencia de Rescate Óptima Encontrada (14 Ticks)
Todos los algoritmos alcanzaron la solución óptima absoluta: **3 víctimas rescatadas en 14 ticks**.
1. **Tick 0:** Inicio en `(1, 1)`
2. **Tick 1 a 3 (E, E, E):** Arribo a `(1, 4)` en Tick 3 -> **Rescate exitoso de V1** (Límite: 5 ticks).
3. **Tick 4 a 6 (S, S, S):** Desplazamiento por pasillo central.
4. **Tick 7 (E):** Arribo a `(4, 5)` en Tick 7 -> **Rescate exitoso de V5** (Límite: 7 ticks, salvada in extremis).
5. **Tick 8 a 13 (E, N, N, N, E, E):** Rodeo por el ala este.
6. **Tick 14 (S):** Arribo a `(2, 8)` en Tick 14 -> **Rescate exitoso de V4** (Límite: 20 ticks).
7. **Víctimas no rescatadas:** `V3` (3 ticks en `(5, 2)`) y `V2` (12 ticks en celda no transitable `(3, 7)`).

### 6.3 Análisis de Eficiencia
- **A\* frente a BFS/UCS:** A\* expandió solo **99 nodos**, representando una reducción del **80.5% en expansiones de memoria** en comparación con los 509 nodos de BFS y UCS. Esto evidencia la eficacia de la heurística $h(n)$ al orientar la búsqueda hacia el objetivo prometedor.
- **IDDFS:** Aunque su requerimiento de memoria es mínimo ($O(d)$), expande un número significativamente mayor de nodos (541,204) debido a la regeneración reiterativa del árbol de búsqueda en cada cota de profundidad.

---

## 7. Experimentos con Mapas de Prueba Adicionales

### 7.1 Mapa Simple (`data/mapa_simple.txt`)
- Dimensiones: $4 \times 7$. 2 víctimas (`V1` en `(1, 5)` con 6 ticks, `V2` en `(3, 4)` con 12 ticks).
- **Resultado:** Los 4 algoritmos salvaron al **100% de las víctimas (2/2)** en 9 ticks.
- **Nodos A\*:** 18 nodos vs 42 nodos de BFS.

### 7.2 Mapa Trampa / Callejón sin Salida (`data/mapa_trampa.txt`)
- Contiene una víctima "señuelo" en un fondo de saco (`V_trampa`) y dos víctimas en el corredor principal.
- **Resultado:** Los algoritmos informados con poda ($A^*$) evitan explorar a fondo el callejón de la víctima trampa si el tiempo no permite salvar a las demás, priorizando la ruta de mayor supervivencia global.

---

## 8. Conclusiones

1. **Modelado del Espacio de Estados:** La inclusión explícita del conjunto de víctimas rescatadas y del tick actual en la 4-tupla del estado fue determinante para garantizar que el grafo de búsqueda no podara soluciones de mayor calidad que pasaran por la misma coordenada espacial.
2. **Superioridad de la Búsqueda Informada ($A^*$):** La incorporación de la heurística admisible basada en víctimas condenadas redujo drásticamente el espacio de búsqueda en más de un 80%, manteniendo la garantía matemática de optimalidad.
3. **Poda Temprana por Alcanzabilidad:** La detección de víctimas inalcanzables mediante cota Manhattan permitió truncar ramas inviables de forma anticipada, evitando la explosión combinatoria del reloj de simulación.
4. **Cumplimiento de Restricciones:** El proyecto fue construido en su totalidad con bibliotecas nativas de Python (sin frameworks de terceros), satisfaciendo rigurosamente las pautas de evaluación y los criterios de diseño de software modular.

