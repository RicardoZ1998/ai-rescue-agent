import os
from typing import Dict, Tuple
from src.modelos_de_datos import MapaDelEntorno, VictimaEnRiesgo

def cargar_mapa_desde_archivo(ruta_del_archivo_de_mapa: str) -> MapaDelEntorno:
    if not os.path.exists(ruta_del_archivo_de_mapa):
        raise FileNotFoundError(f"No se encontró el archivo de mapa en: {ruta_del_archivo_de_mapa}")

    with open(ruta_del_archivo_de_mapa, 'r', encoding='utf-8') as archivo_mapa:
        lineas_del_archivo = [linea.rstrip('\r\n') for linea in archivo_mapa if linea.strip()]

    if not lineas_del_archivo:
        raise ValueError("El archivo de mapa está vacío.")

    ancho_esperado_de_la_cuadricula = len(lineas_del_archivo[0])
    posicion_inicial_del_agente = None

    for indice_fila, contenido_de_la_fila in enumerate(lineas_del_archivo):
        if len(contenido_de_la_fila) != ancho_esperado_de_la_cuadricula:
            raise ValueError(f"Fila {indice_fila} tiene longitud {len(contenido_de_la_fila)}, se esperaba {ancho_esperado_de_la_cuadricula}.")
        
        for indice_columna, caracter_de_la_celda in enumerate(contenido_de_la_fila):
            if caracter_de_la_celda == 'S':
                if posicion_inicial_del_agente is not None:
                    raise ValueError(f"Existe más de una posición de inicio 'S' en el mapa (encontrada en {(indice_fila, indice_columna)}).")
                posicion_inicial_del_agente = (indice_fila, indice_columna)

    if posicion_inicial_del_agente is None:
        raise ValueError("No se encontró la posición de inicio 'S' en el mapa.")

    return MapaDelEntorno(celdas_del_mapa=lineas_del_archivo, posicion_de_inicio=posicion_inicial_del_agente)


def cargar_victimas_desde_archivo(ruta_del_archivo_de_victimas: str, mapa_del_entorno: MapaDelEntorno = None) -> Dict[str, VictimaEnRiesgo]:
    if not os.path.exists(ruta_del_archivo_de_victimas):
        raise FileNotFoundError(f"No se encontró el archivo de víctimas en: {ruta_del_archivo_de_victimas}")

    diccionario_de_victimas: Dict[str, VictimaEnRiesgo] = {}

    with open(ruta_del_archivo_de_victimas, 'r', encoding='utf-8') as archivo_victimas:
        lineas_del_archivo = [linea.strip() for linea in archivo_victimas if linea.strip()]

    if not lineas_del_archivo:
        raise ValueError("El archivo de víctimas está vacío.")

    primera_linea_separada = lineas_del_archivo[0].lower().split(',')
    indice_donde_empiezan_los_datos = 0
    if len(primera_linea_separada) >= 4 and 'id' in primera_linea_separada[0]:
        indice_donde_empiezan_los_datos = 1

    for numero_de_linea, contenido_de_la_linea in enumerate(lineas_del_archivo[indice_donde_empiezan_los_datos:], start=indice_donde_empiezan_los_datos + 1):
        campos_separados_por_coma = [campo.strip() for campo in contenido_de_la_linea.split(',')]
        if len(campos_separados_por_coma) < 4:
            raise ValueError(f"Línea {numero_de_linea} inválida en víctimas: '{contenido_de_la_linea}'. Se esperan 4 columnas.")

        identificador_de_victima = campos_separados_por_coma[0]
        texto_fila = campos_separados_por_coma[1]
        texto_columna = campos_separados_por_coma[2]
        texto_ticks = campos_separados_por_coma[3]

        try:
            fila_de_la_victima = int(texto_fila)
            columna_de_la_victima = int(texto_columna)
            ticks_de_supervivencia = int(texto_ticks)
        except ValueError:
            raise ValueError(f"Línea {numero_de_linea}: Las coordenadas y ticks deben ser enteros. Recibido: {campos_separados_por_coma}")

        if ticks_de_supervivencia < 0:
            raise ValueError(f"Línea {numero_de_linea}: Los ticks de supervivencia no pueden ser negativos.")

        if mapa_del_entorno is not None:
            if not (0 <= fila_de_la_victima < mapa_del_entorno.filas and 0 <= columna_de_la_victima < mapa_del_entorno.columnas):
                raise ValueError(f"Víctima {identificador_de_victima} en ({fila_de_la_victima}, {columna_de_la_victima}) está fuera de los límites del mapa.")
            if mapa_del_entorno.celdas[fila_de_la_victima][columna_de_la_victima] == '#':
                print(f"[ADVERTENCIA] Víctima {identificador_de_victima} en ({fila_de_la_victima}, {columna_de_la_victima}) coincide con un muro '#'. Verifique las coordenadas.")

        diccionario_de_victimas[identificador_de_victima] = VictimaEnRiesgo(identificador_de_victima, fila_de_la_victima, columna_de_la_victima, ticks_de_supervivencia)

    return diccionario_de_victimas

