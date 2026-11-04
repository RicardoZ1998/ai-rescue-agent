import tkinter as tk
from src.interfaz_grafica.ventana_principal import AplicacionDeRescate

def test_instanciacion_gui():
    print("--- 1. Probando inicialización de la ventana Tkinter y widgets ---")
    ventana_de_prueba = tk.Tk()
    ventana_de_prueba.withdraw()
    
    aplicacion_de_rescate = AplicacionDeRescate(ventana_de_prueba)
    
    assert aplicacion_de_rescate.combo_algoritmo.get() == "A*", "El algoritmo por defecto debe ser A*"
    assert int(aplicacion_de_rescate.scale_velocidad.get()) in (250, 300), "La velocidad por defecto debe ser válida"
    assert aplicacion_de_rescate.btn_iniciar is not None, "El botón Iniciar Rescate debe existir"
    assert aplicacion_de_rescate.btn_comparar_todos is not None, "El botón Comparar los 4 Algoritmos debe existir"
    assert aplicacion_de_rescate.canvas is not None, "El canvas de simulación debe existir"
    assert aplicacion_de_rescate.tree_comparacion is not None, "La tabla Treeview comparativa debe existir"
    
    ventana_de_prueba.destroy()
    print(" [OK] Ventana, Canvas animado y Tabla Comparativa validados exitosamente.")

if __name__ == "__main__":
    test_instanciacion_gui()
    print("\n>>> ¡TODOS LOS TESTS DE LA TARJETA 4.3 PASARON CON ÉXITO! <<<")
