"""
Módulo de modelos de datos básicos para el problema del Agente de Rescate.
"""

# Importa los "tipos" que se usan en las anotaciones (List, Tuple, Set).
# Las anotaciones solo documentan; Python no las obliga a cumplirse al ejecutar.
from typing import List, Tuple, Set

# Clase que representa a UNA víctima (un dato fijo: no cambia durante la búsqueda).
class Victima:
    """
    Representa una víctima en el mapa con su ubicación y tiempo de supervivencia límite.
    """
    # Constructor: se ejecuta al crear una víctima, p. ej. Victima("V1", 1, 4, 5).
    def __init__(self, id_victima: str, fila: int, columna: int, ticks_supervivencia: int):
        # Guarda el identificador de la víctima (texto como "V1").
        self.id = id_victima
        # Guarda la fila de la cuadrícula donde está la víctima.
        self.fila = fila
        # Guarda la columna de la cuadrícula donde está la víctima.
        self.columna = columna
        # Guarda el último tick en el que aún se puede rescatar (si llegas con tick <= este valor, se salva).
        self.ticks_supervivencia = ticks_supervivencia

    # Método especial que define cómo se muestra el objeto al imprimirlo o verlo en el depurador.
    def __repr__(self) -> str:
        # Devuelve un texto como "Victima(V1, pos=(1, 4), ticks=5)".
        return f"Victima({self.id}, pos=({self.fila}, {self.columna}), ticks={self.ticks_supervivencia})"


# Clase que representa el mapa (la cuadrícula). Tampoco cambia durante la búsqueda.
class Mapa:
    """
    Representa la cuadrícula 2D del desastre.
    - '#' = pared
    - '.' = celda libre
    - 'S' = posición inicial del agente
    """
    # Constructor: recibe la lista de filas (strings) y la posición inicial ya calculada.
    def __init__(self, celdas: List[str], inicio: Tuple[int, int]):
        # Guarda la lista de strings; cada string es una fila del mapa (ej. "#S...#...#").
        self.celdas = celdas
        # Número de filas = cantidad de strings en la lista.
        self.filas = len(celdas)
        # Número de columnas = largo de la primera fila (si no hay filas, 0 para no fallar).
        self.columnas = len(celdas[0]) if self.filas > 0 else 0
        # Guarda la posición inicial del agente como tupla (fila, columna).
        self.inicio = inicio  # (fila, columna)

    # Pregunta: ¿puede el agente pararse en (fila, columna)?
    def es_posicion_valida(self, fila: int, columna: int) -> bool:
        """Verifica si las coordenadas están dentro del mapa y no son una pared."""
        # Primero comprueba que la coordenada esté dentro de los límites del mapa
        # (así evita errores de índice al consultar self.celdas).
        if 0 <= fila < self.filas and 0 <= columna < self.columnas:
            # Dentro del mapa: es válida si la celda NO es una pared '#'.
            return self.celdas[fila][columna] != '#'
        # Fuera del mapa: no es válida.
        return False

    # Texto de depuración del mapa.
    def __repr__(self) -> str:
        # Devuelve algo como "Mapa(7x10, inicio=(1, 1))".
        return f"Mapa({self.filas}x{self.columnas}, inicio={self.inicio})"


# Clase central del proyecto: un NODO/ESTADO del espacio de búsqueda.
class Estado:
    """
    Definición formal del estado del agente de rescate.
    Estado: (fila, columna, conjunto_de_victimas_vivas, tick_actual)

    Atributos:
    - fila, columna: posición actual del agente en la cuadrícula.
    - victimas_vivas: frozenset con los IDs de las víctimas que no han muerto ni han sido rescatadas.
    - tick_actual: número de movimientos realizados hasta este estado.
    - victimas_rescatadas: frozenset con los IDs de las víctimas rescatadas con éxito.
    - padre: referencia al estado anterior (para reconstruir la ruta de rescate).
    - accion: acción tomada para llegar a este estado ('N', 'S', 'E', 'O').
    """
    # Constructor del estado. Los parámetros con "=" tienen valor por defecto (son opcionales).
    def __init__(
        self,
        # Fila actual del agente.
        fila: int,
        # Columna actual del agente.
        columna: int,
        # IDs de víctimas todavía vivas y no rescatadas (frozenset = conjunto inmutable y hasheable).
        victimas_vivas: frozenset,
        # Cuántos movimientos se han hecho hasta aquí (0 en el estado inicial).
        tick_actual: int = 0,
        # IDs de víctimas ya rescatadas (por defecto, ninguna).
        victimas_rescatadas: frozenset = frozenset(),
        # Estado desde el cual se llegó a este (None en el estado inicial).
        padre: "Estado" = None,
        # Letra de la acción que llevó a este estado (None en el estado inicial).
        accion: str = None
    ):
        # Guarda la fila del agente.
        self.fila = fila
        # Guarda la columna del agente.
        self.columna = columna
        # Guarda las víctimas vivas.
        self.victimas_vivas = victimas_vivas
        # Guarda el tick actual.
        self.tick_actual = tick_actual
        # Guarda las víctimas rescatadas.
        self.victimas_rescatadas = victimas_rescatadas
        # Guarda el enlace al estado padre (sirve para reconstruir el camino al final).
        self.padre = padre
        # Guarda la acción que generó este estado.
        self.accion = accion

    # Método especial: define el "hash" del objeto. Sin él, no se podría meter un Estado en un set()
    # ni usarlo como llave de un diccionario (se requiere para "visitados" y "costos").
    def __hash__(self) -> int:
        """
        Permite usar el Estado en sets (conjuntos de visitados) y como llaves de diccionarios.
        El hash incluye la posición, las víctimas vivas, las rescatadas y el tick.
        """
        # Combina los 5 componentes que identifican el estado en una tupla y devuelve su hash.
        # Nota: "padre" y "accion" NO entran: no definen la identidad del estado.
        return hash((self.fila, self.columna, self.victimas_vivas, self.victimas_rescatadas, self.tick_actual))

    # Método especial: define cuándo dos estados son "iguales" (==). Debe ser coherente con __hash__.
    def __eq__(self, otro: object) -> bool:
        # Si "otro" no es un Estado (ej. un número), no puede ser igual.
        if not isinstance(otro, Estado):
            return False
        # Son iguales si coinciden TODOS los componentes de identidad.
        return (
            # Misma fila
            self.fila == otro.fila and
            # Misma columna
            self.columna == otro.columna and
            # Mismas víctimas vivas
            self.victimas_vivas == otro.victimas_vivas and
            # Mismas víctimas rescatadas
            self.victimas_rescatadas == otro.victimas_rescatadas and
            # Mismo tick
            self.tick_actual == otro.tick_actual
        )

    # Función sucesora: dado este estado, produce todos los estados a los que se puede llegar en 1 movimiento.
    def generar_sucesores(self, mapa: Mapa, dict_victimas: dict) -> List["Estado"]:
        """
        Genera los estados sucesores válidos aplicando las 4 acciones cardinales:
        Norte (-1, 0), Sur (1, 0), Este (0, 1), Oeste (0, -1).

        Reglas:
        1. El agente no puede moverse a celdas con pared '#'.
        2. Cada movimiento incrementa el tick en 1 (costo = 1 tick).
        3. Si la nueva posición coincide con una víctima viva y tick_nuevo <= tick_supervivencia, es rescatada.
        4. Cualquier víctima viva cuyo tiempo expire (tick_nuevo > tick_supervivencia) muere en este turno.
        """
        # Lista donde se acumularán los estados sucesores válidos.
        sucesores = []
        # Las 4 acciones posibles: (letra, cambio en fila, cambio en columna).
        movimientos = [
            # Norte: sube una fila (la fila 0 es la de arriba).
            ('N', -1, 0),
            # Sur: baja una fila.
            ('S', 1, 0),
            # Este: una columna a la derecha.
            ('E', 0, 1),
            # Oeste ('O'): una columna a la izquierda.
            ('O', 0, -1)
        ]

        # Todo movimiento cuesta 1 tick, así que el tick de TODOS los sucesores es el actual + 1.
        nuevo_tick = self.tick_actual + 1

        # Recorre cada una de las 4 acciones (df = delta fila, dc = delta columna).
        for accion, df, dc in movimientos:
            # Calcula la fila a la que llegaría el agente.
            nueva_fila = self.fila + df
            # Calcula la columna a la que llegaría el agente.
            nueva_col = self.columna + dc

            # Si esa celda es pared o está fuera del mapa, esta acción no es válida: salta a la siguiente.
            if not mapa.es_posicion_valida(nueva_fila, nueva_col):
                continue

            # Copia mutable de las rescatadas actuales (set normal) para poder agregarle la nueva rescatada.
            nuevas_rescatadas = set(self.victimas_rescatadas)
            # Conjunto vacío donde se guardarán las víctimas que siguen vivas tras este movimiento.
            nuevas_vivas = set()

            # Revisa cada víctima que seguía viva en el estado actual.
            for id_v in self.victimas_vivas:
                # Busca el objeto Victima a partir de su id (para conocer posición y tiempo límite).
                v = dict_victimas[id_v]
                
                # ¿El agente pisa justo la celda de esta víctima?
                if v.fila == nueva_fila and v.columna == nueva_col:
                    # Sí la pisa: se rescata solo si llega a tiempo (tick nuevo <= su límite).
                    if nuevo_tick <= v.ticks_supervivencia:
                        # Llegó a tiempo: pasa a rescatadas (y NO se agrega a vivas).
                        nuevas_rescatadas.add(id_v)
                    # Si llegó tarde, no entra a ninguno de los dos conjuntos: queda como fallecida.
                # El agente NO está en la celda de esta víctima.
                else:
                    # Sigue viva solo si todavía no se le acaba el tiempo en el nuevo tick.
                    if nuevo_tick <= v.ticks_supervivencia:
                        # Aún le queda tiempo: continúa en el conjunto de vivas.
                        nuevas_vivas.add(id_v)
                    # Si ya se pasó de tiempo, muere (no se agrega a ningún conjunto).

            # Construye el nuevo estado con la posición nueva, los conjuntos actualizados y el tick + 1.
            nuevo_estado = Estado(
                # Nueva fila del agente.
                fila=nueva_fila,
                # Nueva columna del agente.
                columna=nueva_col,
                # Se convierte a frozenset para que sea inmutable y hasheable.
                victimas_vivas=frozenset(nuevas_vivas),
                # Tick incrementado.
                tick_actual=nuevo_tick,
                # Rescatadas actualizadas, también como frozenset.
                victimas_rescatadas=frozenset(nuevas_rescatadas),
                # El padre del nuevo estado es el estado actual (self): así se podrá reconstruir la ruta.
                padre=self,
                # Guarda la letra de la acción tomada.
                accion=accion
            )
            # Agrega el nuevo estado a la lista de sucesores.
            sucesores.append(nuevo_estado)

        # Devuelve todos los sucesores válidos (entre 0 y 4).
        return sucesores

    # Reconstruye la ruta desde el estado inicial hasta este estado, siguiendo los "padre" hacia atrás.
    def reconstruir_camino(self) -> List[Tuple[str, int, int]]:
        """
        Reconstruye la secuencia de pasos desde el estado inicial hasta este estado.
        Retorna una lista de tuplas: (accion, fila, columna).
        """
        # Lista donde se irán guardando los pasos (quedará en orden inverso al principio).
        camino = []
        # Empieza en este estado (el final de la ruta).
        actual = self
        # Sube por la cadena de padres hasta llegar al estado inicial (cuyo padre es None).
        while actual is not None:
            # Guarda el paso: (acción que llevó aquí, fila, columna).
            camino.append((actual.accion, actual.fila, actual.columna))
            # Sube un nivel: pasa al estado padre.
            actual = actual.padre
        # Se construyó del final al inicio; se invierte para que quede de inicio a final.
        camino.reverse()
        # Devuelve la ruta (el primer elemento es el inicio, con acción None).
        return camino

    # Texto de depuración del estado.
    def __repr__(self) -> str:
        # Devuelve algo como "Estado(pos=(1, 1), tick=0, vivas={...}, rescatadas={...})".
        return (
            # Posición del agente.
            f"Estado(pos=({self.fila}, {self.columna}), "
            # Tick actual.
            f"tick={self.tick_actual}, "
            # Víctimas vivas (se convierte a set normal para que se imprima más limpio).
            f"vivas={set(self.victimas_vivas)}, "
            # Víctimas rescatadas.
            f"rescatadas={set(self.victimas_rescatadas)})"
        )