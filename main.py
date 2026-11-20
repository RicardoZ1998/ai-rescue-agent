"""
Punto de entrada principal del Agente de Rescate con Víctimas en Riesgo.
Lanza la interfaz gráfica de escritorio con Tkinter.
"""

# Importa tkinter (biblioteca estándar de Python para interfaces de escritorio)
# y le pone el alias "tk" para escribir menos.
import tkinter as tk
# Importa la clase AppRescate, que contiene toda la ventana y la lógica de la GUI.
from src.gui.app import AppRescate

# Función que arma y lanza la aplicación.
def main():
    # Crea la ventana raíz (la ventana principal) de Tkinter.
    root = tk.Tk()
    # Crea la aplicación: le pasa la ventana raíz para que construya adentro todos los widgets.
    app = AppRescate(root)
    # Arranca el bucle de eventos: mantiene la ventana abierta y atiende clics, timers, etc.
    # El programa se queda aquí hasta que se cierra la ventana.
    root.mainloop()

# Esta condición es True solo si el archivo se ejecuta directamente (python main.py),
# y es False si alguien lo importa desde otro archivo.
if __name__ == "__main__":
    # Llama a la función principal para iniciar el programa.
    main()