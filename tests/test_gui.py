"""
Pruebas de validación de maquetación y animación de la Interfaz Gráfica Tkinter (Tarjeta 4.2).
"""

import tkinter as tk
from src.gui.app import AppRescate

def test_instanciacion_gui():
    print("--- 1. Probando inicialización de la ventana Tkinter y widgets ---")
    root = tk.Tk()
    root.withdraw()
    
    app = AppRescate(root)
    
    assert app.combo_algoritmo.get() == "A*", "El algoritmo por defecto debe ser A*"
    assert int(app.scale_velocidad.get()) in (250, 300), "La velocidad por defecto debe ser válida"
    assert app.btn_iniciar is not None, "El botón Iniciar Rescate debe existir"
    assert app.btn_pausa is not None, "El botón Pausar debe existir"
    assert app.btn_reiniciar is not None, "El botón Reiniciar debe existir"
    assert app.canvas is not None, "El canvas de simulación debe existir"
    
    root.destroy()
    print(" [OK] Ventana, controles de animación y Canvas validados exitosamente.")

if __name__ == "__main__":
    test_instanciacion_gui()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 4.2 PASARON CON ÉXITO! <<<")
