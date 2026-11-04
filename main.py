"""
Punto de entrada principal del Agente de Rescate con Víctimas en Riesgo.
Lanza la interfaz gráfica de escritorio con Tkinter.
"""

import tkinter as tk
from src.gui.app import AppRescate

def main():
    root = tk.Tk()
    app = AppRescate(root)
    root.mainloop()

if __name__ == "__main__":
    main()
