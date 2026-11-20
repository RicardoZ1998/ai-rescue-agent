# Este archivo __init__.py convierte la carpeta "gui" en un paquete de Python.
# Re-exporta la clase principal de la interfaz para poder importarla como "from src.gui import AppRescate".

# Importa la clase AppRescate desde el módulo app.py.
from src.gui.app import AppRescate

# Lista de nombres públicos del paquete (lo que se exporta con "import *").
__all__ = ["AppRescate"]