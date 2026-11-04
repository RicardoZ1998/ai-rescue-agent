# Guía Maestra para la Sustentación Individual
## Agente de Rescate con Víctimas en Riesgo - Inteligencia Artificial

---

## 🎯 Bloque 1: El Espacio de Estados y la Representación

### ❓ Pregunta 1: *"¿Por qué el estado no puede ser simplemente la posición `(x, y)` del agente en la cuadrícula?"*
> **Tu respuesta:**
> *"Porque este es un problema dinámico con restricciones temporales. Si el estado fuera solo `(x, y)`, el algoritmo asumiría que estar en la casilla `(3, 4)` en el tick 2 con 5 víctimas vivas es el mismo estado que estar en `(3, 4)` en el tick 15 cuando ya murieron 4 víctimas. El conjunto de visitados podaría el camino creyendo erróneamente que ya pasó por ahí.
> 
> Por eso el estado formal es una tupla:
> `(fila, columna, victimas_vivas, victimas_rescatadas, tick_actual)`."*

---

### ❓ Pregunta 2: *"¿Por qué usan `frozenset` para las víctimas en vez de una lista o un `set` común de Python?"*
> **Tu respuesta:**
> *"Por la necesidad de **inmutabilidad y hashing**. En Python, los algoritmos de búsqueda necesitan almacenar los estados en un conjunto de visitados (`set`) o en diccionarios para consultas en tiempo $O(1)$. Un `set` o una lista ordinaria son objetos mutables, por lo que Python no les permite calcular su `__hash__` (daría `TypeError: unhashable type: 'set'`). Al usar `frozenset`, garantizamos que la colección de víctimas sea inmutable y por ende estrictamente hasheable."*

---

### ❓ Pregunta 3: *"¿Qué pasa si quitas `victimas_rescatadas` del hash del estado?"*
> **Tu respuesta:**
> *"Ocurriría un error de poda subóptima. Si el agente llega a la misma coordenada `(r, c)` en el mismo `tick`, pero por un camino rescató a 2 víctimas y por otro camino solo rescató a 1 víctima, ambos estados tendrían el mismo hash y la misma posición. Si no incluimos `victimas_rescatadas`, el algoritmo descartaría el camino con más rescates si se explora de segundo creyendo que ya visitó ese estado."*

---

## 🎯 Bloque 2: Función Sucesora y Criterios de Parada

### ❓ Pregunta 4: *"¿Cómo sabe el algoritmo cuándo detenerse si no hay una coordenada fija de meta?"*
> **Tu respuesta:**
> *"En la función `es_estado_objetivo(estado)`. La búsqueda se detiene cuando ya no queda ninguna víctima viva alcanzable:
> 1. Si `len(estado.victimas_vivas) == 0` (todas fueron rescatadas o murieron).
> 2. O si para todas las víctimas vivas restantes se cumple que:
>    $$\text{distancia\_Manhattan}(agente, v) > \text{ticks\_restantes}(v)$$
> Si ninguna víctima viva puede ser alcanzada físicamente antes de que su tiempo expire, la rama se declara terminal y se detiene la expansión."*

---

### ❓ Pregunta 5: *"¿Cómo se desempata entre dos soluciones que llegan a la meta?"*
> **Tu respuesta:**
> *"Aplicamos el criterio de dos niveles del enunciado con la función `es_mejor_solucion(candidato, actual_mejor)`:
> 1. **Criterio principal:** Maximizar el número de víctimas rescatadas (`len(rescatadas)`).
> 2. **Criterio de desempate:** A igual número de víctimas rescatadas, gana la ruta con **menor número de ticks** (`tick_actual`)."*

---

## 🎯 Bloque 3: Heurística y Algoritmo A*

### ❓ Pregunta 6: *"Demuéstreme verbalmente por qué su heurística $h(n)$ es admisible."*
> **Tu respuesta:**
> *"Una heurística es admisible si nunca sobreestima el costo real: $h(n) \le h^*(n)$.
> En nuestro problema, el costo a minimizar son las muertes de víctimas.
> Nuestra heurística define que una víctima está condenada si su distancia Manhattan al agente es estrictamente mayor que sus ticks de vida restantes:
> $$D_M(agente, v) > t_{rest}(v)$$
> Dado que la distancia Manhattan en una cuadrícula con obstáculos es la distancia mínima absoluta en línea recta, cualquier ruta real con muros tomará $D_{real} \ge D_M$.
> Por lo tanto, si ni siquiera en línea recta el agente llega a tiempo, es físicamente imposible salvarla en el mapa real. Como solo contamos víctimas cuya muerte es $100\%$ segura e inevitable, $h(n)$ jamás sobreestima las muertes reales, demostrando formalmente que es **admisible**."*

---

### ❓ Pregunta 7: *"¿Por qué A* expande solo 99 nodos mientras BFS y UCS expandieron 509 nodos?"*
> **Tu respuesta:**
> *"Porque BFS y UCS son algoritmos ciegos (no informados): exploran en todas direcciones de forma isotrópica sin saber dónde están los objetivos ni cuáles van a morir primero.
> A* combina el costo real acumulado $g(n)$ con la estimación heurística $h(n)$, priorizando siempre las ramas que minimizan las muertes condenadas y que se dirigen hacia la víctima viva más cercana. Esto permite 'podar' y postergar ramas que van en direcciones inútiles, reduciendo en más de un 80% las expansiones de nodos sin perder la garantía de optimalidad."*

---

## 🎯 Bloque 4: Modificaciones en Vivo Típicas (Live Coding)

### 💻 Caso A: *"Cambie el costo por paso de 1 tick a 2 ticks"*
> **Qué hacer en el código:**
> Vas a [`src/modelos_de_datos.py`](file:///c:/Users/Ricar/Documents/GitHub/ai-rescue-agent/src/modelos_de_datos.py), dentro del método `generar_estados_sucesores`:
> Cambias:
> ```python
> tick_despues_del_movimiento = self.tick_actual + 1
> ```
> Por:
> ```python
> tick_despues_del_movimiento = self.tick_actual + 2
> ```
> ¡Y listo! Todas las transiciones, muertes y rescates se adaptarán automáticamente a 2 ticks por paso.

---

### 💻 Caso B: *"Permita que el agente se mueva en diagonales"*
> **Qué hacer en el código:**
> Vas a [`src/modelos_de_datos.py`](file:///c:/Users/Ricar/Documents/GitHub/ai-rescue-agent/src/modelos_de_datos.py), en la lista `direcciones_cardinales_posibles` dentro de `generar_estados_sucesores`:
> Agregas las 4 diagonales:
> ```python
> direcciones_cardinales_posibles = [
>     ('Norte', -1, 0), ('Sur', 1, 0), ('Este', 0, 1), ('Oeste', 0, -1),
>     ('Noreste', -1, 1), ('Noroeste', -1, -1), ('Sureste', 1, 1), ('Suroeste', 1, -1)
> ]
> ```

---

### 💻 Caso C: *"Muestre el camino recorrido con una línea o rastro en el Canvas"*
> **Qué hacer en el código:**
> En [`src/interfaz_grafica/ventana_principal.py`](file:///c:/Users/Ricar/Documents/GitHub/ai-rescue-agent/src/interfaz_grafica/ventana_principal.py), dentro de `_siguiente_paso_animacion`, cada vez que el agente da un paso se puede dibujar un pequeño punto o línea en el canvas con `self.canvas.create_line(...)`.
