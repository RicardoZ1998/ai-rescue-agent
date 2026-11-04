"""
Pruebas de validación de maquetación de la Interfaz Gráfica Tkinter (Tarjeta 4.1).
Valida instanciación y widgets sin bloquear con mainloop.
"""

import tkinter as tk
from src.gui.app import AppRescate

def test_instanciacion_gui():
    print("--- 1. Probando inicialización de la ventana Tkinter y widgets ---")
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana durante el test automático
    
    app = AppRescate(root)
    
    assert app.combo_algoritmo.get() == "A*", "El algoritmo por defecto debe ser A*"
    assert app.scale_velocidad.get() == 250, "La velocidad por defecto debe ser 250 ms"
    assert app.btn_iniciar is not None, "El botón Iniciar Rescate debe existir"
    assert app.canvas is not None, "El canvas de simulación debe existir"
    
    root.destroy()
    print(" [OK] Ventana y componentes creados exitosamente.")

if __name__ == "__main__":
    test_instanciacion_gui()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 4.1 PASARON CON ÉXITO! <<<")

