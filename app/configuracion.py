import json
from pathlib import Path

class GestorConfiguracion:
    def __init__(self, ruta_relativa="config/tarifas.json"):
        # Localiza el archivo de tarifas en la raíz del proyecto
        self.ruta_archivo = Path(__file__).resolve().parent.parent / ruta_relativa

    def cargar_tarifas(self):
        try:
            if self.ruta_archivo.exists():
                with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        
        # Valores por defecto si falla o no existe
        return {
            "TARIFA_PARADO": 0.02,
            "TARIFA_MOVIMIENTO": 0.05
        }