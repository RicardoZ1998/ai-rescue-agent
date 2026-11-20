"""
Módulo de carga y validación de archivos mapa.txt y victimas.txt.
No utiliza librerías externas.
"""

# Módulo estándar "os": se usa para comprobar si un archivo existe.
import os
# Tipos para anotaciones (Dict para el diccionario de víctimas; Tuple no se usa realmente aquí).
from typing import Dict, Tuple
# Clases propias: Mapa (la cuadrícula) y Victima (cada víctima).
from src.models import Mapa, Victima

# Lee mapa.txt, lo valida y devuelve un objeto Mapa.
def cargar_mapa(ruta_mapa: str) -> Mapa:
    """
    Carga y valida el archivo mapa.txt.
    Retorna una instancia de Mapa con la matriz y la posición inicial 'S'.
    """
    # Si la ruta no existe en el disco, lanza un error claro (la GUI lo muestra en un cuadro).
    if not os.path.exists(ruta_mapa):
        raise FileNotFoundError(f"No se encontró el archivo de mapa en: {ruta_mapa}")

    # Abre el archivo en modo lectura ('r') con codificación UTF-8; "with" lo cierra solo al terminar.
    with open(ruta_mapa, 'r', encoding='utf-8') as f:
        # Recorre cada línea: descarta las vacías (linea.strip() vacío = False) y
        # le quita el salto de línea del final (\r\n) a las demás. Resultado: lista de filas.
        lineas = [linea.rstrip('\r\n') for linea in f if linea.strip()]

    # Si no quedó ninguna línea, el archivo estaba vacío: error.
    if not lineas:
        raise ValueError("El archivo de mapa está vacío.")

    # Validar que todas las filas tengan la misma longitud
    # Toma como ancho esperado el largo de la primera fila.
    ancho = len(lineas[0])
    # Aquí se guardará la posición de 'S'; empieza en None (= "aún no encontrada").
    pos_inicio = None

    # Recorre las filas con su índice i (número de fila).
    for i, fila in enumerate(lineas):
        # Si alguna fila tiene distinto largo que la primera, el mapa no es rectangular: error.
        if len(fila) != ancho:
            raise ValueError(f"Fila {i} tiene longitud {len(fila)}, se esperaba {ancho}.")
        
        # Recorre cada carácter de la fila con su índice j (número de columna).
        for j, caracter in enumerate(fila):
            # ¿Este carácter es la posición inicial 'S'?
            if caracter == 'S':
                # Si ya se había encontrado otra 'S' antes, hay más de una: error.
                if pos_inicio is not None:
                    raise ValueError(f"Existe más de una posición de inicio 'S' en el mapa (encontrada en {(i, j)}).")
                # Primera 'S' encontrada: guarda su posición (fila, columna).
                pos_inicio = (i, j)

    # Si terminó de recorrer todo y nunca vio una 'S', error.
    if pos_inicio is None:
        raise ValueError("No se encontró la posición de inicio 'S' en el mapa.")

    # Crea y devuelve el Mapa con las filas leídas y la posición inicial encontrada.
    return Mapa(celdas=lineas, inicio=pos_inicio)


# Lee victimas.txt, lo valida y devuelve un diccionario {id: Victima}.
def cargar_victimas(ruta_victimas: str, mapa: Mapa = None) -> Dict[str, Victima]:
    """
    Carga y valida el archivo victimas.txt.
    Estructura esperada: id,fila,columna,ticks_supervivencia
    Retorna un diccionario de {id: Victima}.
    Si se provee el mapa, valida que no estén sobre paredes ni fuera de rango.
    """
    # Si el archivo no existe, error claro.
    if not os.path.exists(ruta_victimas):
        raise FileNotFoundError(f"No se encontró el archivo de víctimas en: {ruta_victimas}")

    # Diccionario resultado, vacío al inicio: llave = id de víctima, valor = objeto Victima.
    victimas: Dict[str, Victima] = {}

    # Abre el archivo de víctimas en lectura con UTF-8.
    with open(ruta_victimas, 'r', encoding='utf-8') as f:
        # Lista de líneas sin espacios/saltos en los bordes (strip) y sin líneas vacías.
        lineas = [linea.strip() for linea in f if linea.strip()]

    # Si no hay líneas, el archivo está vacío: error.
    if not lineas:
        raise ValueError("El archivo de víctimas está vacío.")

    # Ignorar encabezado si existe (id,fila,...)
    # Separa la primera línea por comas, en minúsculas, para decidir si es el encabezado.
    primera_linea = lineas[0].lower().split(',')
    # Por defecto, los datos empiezan en la primera línea (índice 0).
    indice_inicio = 0
    # Si la primera línea tiene 4+ columnas y la primera columna contiene "id", es el encabezado.
    if len(primera_linea) >= 4 and 'id' in primera_linea[0]:
        # Entonces los datos reales empiezan en la segunda línea (índice 1).
        indice_inicio = 1

    # Recorre solo las líneas de datos; num_linea sirve para decir en qué línea está el error.
    for num_linea, linea in enumerate(lineas[indice_inicio:], start=indice_inicio + 1):
        # Divide la línea por comas y le quita espacios a cada pedazo.
        partes = [p.strip() for p in linea.split(',')]
        # Si hay menos de 4 columnas, la línea está incompleta: error.
        if len(partes) < 4:
            raise ValueError(f"Línea {num_linea} inválida en víctimas: '{linea}'. Se esperan 4 columnas.")

        # Desempaqueta las 4 primeras columnas en variables (aún como texto).
        id_v, str_fila, str_col, str_ticks = partes[0], partes[1], partes[2], partes[3]

        # Intenta convertir fila, columna y ticks de texto a número entero.
        try:
            # Convierte la fila a entero.
            fila = int(str_fila)
            # Convierte la columna a entero.
            col = int(str_col)
            # Convierte los ticks de supervivencia a entero.
            ticks = int(str_ticks)
        # Si alguna conversión falla (ej. "abc"), captura el error de conversión.
        except ValueError:
            # Lanza un error con mensaje claro indicando la línea y los valores recibidos.
            raise ValueError(f"Línea {num_linea}: Las coordenadas y ticks deben ser enteros. Recibido: {partes}")

        # Un tiempo de supervivencia negativo no tiene sentido físico: error.
        if ticks < 0:
            raise ValueError(f"Línea {num_linea}: Los ticks de supervivencia no pueden ser negativos.")

        # Validaciones con respecto al mapa
        # Solo se validan contra el mapa si la GUI/el test pasó un mapa ya cargado.
        if mapa is not None:
            # Si la víctima cae fuera de la cuadrícula, error.
            if not (0 <= fila < mapa.filas and 0 <= col < mapa.columnas):
                raise ValueError(f"Víctima {id_v} en ({fila}, {col}) está fuera de los límites del mapa.")
            # Si cae sobre un muro, NO se detiene: solo imprime una advertencia en consola.
            if mapa.celdas[fila][col] == '#':
                print(f"[ADVERTENCIA] Víctima {id_v} en ({fila}, {col}) coincide con un muro '#'. Verifique las coordenadas.")

        # Crea el objeto Victima y lo guarda en el diccionario usando su id como llave.
        victimas[id_v] = Victima(id_v, fila, col, ticks)

    # Devuelve el diccionario completo de víctimas.
    return victimas