"""
Módulo de carga y validación de archivos mapa.txt y victimas.txt.
No utiliza librerías externas.
"""

import os
from typing import Dict, Tuple
from src.models import Mapa, Victima

def cargar_mapa(ruta_mapa: str) -> Mapa:
    """
    Carga y valida el archivo mapa.txt.
    Retorna una instancia de Mapa con la matriz y la posición inicial 'S'.
    """
    if not os.path.exists(ruta_mapa):
        raise FileNotFoundError(f"No se encontró el archivo de mapa en: {ruta_mapa}")

    with open(ruta_mapa, 'r', encoding='utf-8') as f:
        lineas = [linea.rstrip('\r\n') for linea in f if linea.strip()]

    if not lineas:
        raise ValueError("El archivo de mapa está vacío.")

    # Validar que todas las filas tengan la misma longitud
    ancho = len(lineas[0])
    pos_inicio = None

    for i, fila in enumerate(lineas):
        if len(fila) != ancho:
            raise ValueError(f"Fila {i} tiene longitud {len(fila)}, se esperaba {ancho}.")
        
        for j, caracter in enumerate(fila):
            if caracter == 'S':
                if pos_inicio is not None:
                    raise ValueError(f"Existe más de una posición de inicio 'S' en el mapa (encontrada en {(i, j)}).")
                pos_inicio = (i, j)

    if pos_inicio is None:
        raise ValueError("No se encontró la posición de inicio 'S' en el mapa.")

    return Mapa(celdas=lineas, inicio=pos_inicio)


def cargar_victimas(ruta_victimas: str, mapa: Mapa = None) -> Dict[str, Victima]:
    """
    Carga y valida el archivo victimas.txt.
    Estructura esperada: id,fila,columna,ticks_supervivencia
    Retorna un diccionario de {id: Victima}.
    Si se provee el mapa, valida que no estén sobre paredes ni fuera de rango.
    """
    if not os.path.exists(ruta_victimas):
        raise FileNotFoundError(f"No se encontró el archivo de víctimas en: {ruta_victimas}")

    victimas: Dict[str, Victima] = {}

    with open(ruta_victimas, 'r', encoding='utf-8') as f:
        lineas = [linea.strip() for linea in f if linea.strip()]

    if not lineas:
        raise ValueError("El archivo de víctimas está vacío.")

    # Ignorar encabezado si existe (id,fila,...)
    primera_linea = lineas[0].lower().split(',')
    indice_inicio = 0
    if len(primera_linea) >= 4 and 'id' in primera_linea[0]:
        indice_inicio = 1

    for num_linea, linea in enumerate(lineas[indice_inicio:], start=indice_inicio + 1):
        partes = [p.strip() for p in linea.split(',')]
        if len(partes) < 4:
            raise ValueError(f"Línea {num_linea} inválida en víctimas: '{linea}'. Se esperan 4 columnas.")

        id_v, str_fila, str_col, str_ticks = partes[0], partes[1], partes[2], partes[3]

        try:
            fila = int(str_fila)
            col = int(str_col)
            ticks = int(str_ticks)
        except ValueError:
            raise ValueError(f"Línea {num_linea}: Las coordenadas y ticks deben ser enteros. Recibido: {partes}")

        if ticks < 0:
            raise ValueError(f"Línea {num_linea}: Los ticks de supervivencia no pueden ser negativos.")

        # Validaciones con respecto al mapa
        if mapa is not None:
            if not (0 <= fila < mapa.filas and 0 <= col < mapa.columnas):
                raise ValueError(f"Víctima {id_v} en ({fila}, {col}) está fuera de los límites del mapa.")
            if mapa.celdas[fila][col] == '#':
                print(f"[ADVERTENCIA] Víctima {id_v} en ({fila}, {col}) coincide con un muro '#'. Verifique las coordenadas.")

        victimas[id_v] = Victima(id_v, fila, col, ticks)

    return victimas
