# app/historico.py
from datetime import datetime

class GestorHistorico:
    def __init__(self):
        self.historico = []

    def registrar_carrera(self, duracion_total, coste_total):
        registro = {
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duracion_segundos": round(duracion_total, 2),
            "coste_total": round(coste_total, 2)
        }
        self.historico.append(registro)

    def mostrar_historico_y_caja(self, limpiar_pantalla_func):
        limpiar_pantalla_func()
        print("=========================================")
        print("       HISTÓRICO DE CARRERAS - CAJA      ")
        print("=========================================")
        
        if not self.historico:
            print("No hay carreras registradas todavía en el día.")
        else:
            total_recaudado = 0.0
            for i, carrera in enumerate(self.historico, start=1):
                print(f"Carrera #{i}")
                print(f"  - Fecha/Hora: {carrera['fecha_hora']}")
                print(f"  - Duración:   {carrera['duracion_segundos']} s")
                print(f"  - Coste:      {carrera['coste_total']:.2f} €")
                print("-" * 40)
                total_recaudado += carrera['coste_total']
            
            print(f"\nTOTAL RECAUDADO EN EL DÍA: {total_recaudado:.2f} €")
            print(f"TOTAL DE CARRERAS: {len(self.historico)}")
        
        input("\nPresiona Enter para volver al menú principal...")