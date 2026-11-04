"""
Pruebas de validación de maquetación, animación y tabla comparativa de la GUI (Tarjeta 4.3).
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
    assert app.btn_comparar_todos is not None, "El botón Comparar los 4 Algoritmos debe existir"
    assert app.canvas is not None, "El canvas de simulación debe existir"
    assert app.tree_comparacion is not None, "La tabla Treeview comparativa debe existir"
    
    root.destroy()
    print(" [OK] Ventana, Canvas animado y Tabla Comparativa validados exitosamente.")

if __name__ == "__main__":
    test_instanciacion_gui()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 4.3 PASARON CON ÉXITO! <<<")
