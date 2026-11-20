"""
Pruebas de validación de maquetación, animación y tabla comparativa de la GUI (Tarjeta 4.3).
"""

# Tkinter, necesario para crear la ventana raíz de la prueba.
import tkinter as tk
# La clase de la aplicación que se va a probar.
from src.gui.app import AppRescate

# Prueba única: que la ventana y sus widgets principales se creen correctamente.
def test_instanciacion_gui():
    # Mensaje informativo.
    print("--- 1. Probando inicialización de la ventana Tkinter y widgets ---")
    # Crea la ventana raíz.
    root = tk.Tk()
    # La oculta para que no aparezca en pantalla durante la prueba.
    root.withdraw()
    
    # Crea la aplicación sobre esa ventana.
    app = AppRescate(root)
    
    # El algoritmo seleccionado por defecto debe ser A*.
    assert app.combo_algoritmo.get() == "A*", "El algoritmo por defecto debe ser A*"
    # La velocidad por defecto debe ser 250 o 300 ms.
    assert int(app.scale_velocidad.get()) in (250, 300), "La velocidad por defecto debe ser válida"
    # El botón Iniciar Rescate debe existir.
    assert app.btn_iniciar is not None, "El botón Iniciar Rescate debe existir"
    # El botón Comparar los 4 Algoritmos debe existir.
    assert app.btn_comparar_todos is not None, "El botón Comparar los 4 Algoritmos debe existir"
    # El canvas de simulación debe existir.
    assert app.canvas is not None, "El canvas de simulación debe existir"
    # La tabla comparativa debe existir.
    assert app.tree_comparacion is not None, "La tabla Treeview comparativa debe existir"
    
    # Cierra y destruye la ventana para liberar recursos.
    root.destroy()
    # Mensaje de éxito.
    print(" [OK] Ventana, Canvas animado y Tabla Comparativa validados exitosamente.")

# Ejecución directa del archivo.
if __name__ == "__main__":
    # Ejecuta la prueba.
    test_instanciacion_gui()
    # Mensaje final.
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 4.3 PASARON CON ÉXITO! <<<")