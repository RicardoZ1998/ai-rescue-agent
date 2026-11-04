import tkinter as tk
from src.interfaz_grafica.ventana_principal import AplicacionDeRescate

def main():
    ventana_principal = tk.Tk()
    aplicacion_de_rescate = AplicacionDeRescate(ventana_principal)
    ventana_principal.mainloop()

if __name__ == "__main__":
    main()
