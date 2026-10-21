"""
Punto de entrada de prueba para validar la lectura del mapa y las víctimas (Tarjeta 1.1).
"""

from src.loader import cargar_mapa, cargar_victimas

def main():
    ruta_mapa = "data/mapa.txt"
    ruta_victimas = "data/victimas.txt"

    print("=== PROBANDO LECTURA DE ARCHIVOS ===")
    
    # 1. Cargar Mapa
    mapa = cargar_mapa(ruta_mapa)
    print(f"[OK] Mapa cargado correctamente:")
    print(f"     Dimensiones: {mapa.filas} filas x {mapa.columnas} columnas")
    print(f"     Inicio 'S': fila {mapa.inicio[0]}, columna {mapa.inicio[1]}")
    
    # 2. Cargar Víctimas
    victimas = cargar_victimas(ruta_victimas, mapa=mapa)
    print(f"\n[OK] Víctimas cargadas correctamente ({len(victimas)} encontradas):")
    for v in victimas.values():
        print(f"     - {v.id}: en ({v.fila}, {v.columna}) con {v.ticks_supervivencia} ticks de vida")

    print("\n--- Visualización Rápida en Consola ---")
    # Imprimir mapa con las víctimas superpuestas para verificar
    for r in range(mapa.filas):
        fila_str = []
        for c in range(mapa.columnas):
            # Ver si hay una víctima en esta celda
            vic_aqui = [v.id for v in victimas.values() if v.fila == r and v.columna == c]
            if vic_aqui:
                fila_str.append(vic_aqui[0][0:2]) # V1, V2, etc.
            else:
                fila_str.append(" " + mapa.celdas[r][c])
        print("".join(fila_str))

if __name__ == "__main__":
    main()
