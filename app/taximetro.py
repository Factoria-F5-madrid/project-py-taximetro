import time
import os
from datetime import datetime
from app.historico import GestorHistorico

# ==========================================
# CONFIGURACIÓN DE TARIFAS (US-07 Preparación)
# ==========================================
TARIFAS = {
    "PARADO": 0.02,      # €/segundo (< 20 km/h o parado)
    "MOVIMIENTO": 0.05   # €/segundo
}

class TaximetroMVP:
    def __init__(self):
        self.gestor_caja = GestorHistorico()  # Preparación para US-05
        self.carrera_activa = False
        self.estado_actual = "PARADO"  # "PARADO" o "MOVIMIENTO"
        self.tiempo_inicio_tramo = None
        self.coste_acumulado = 0.0
        self.tiempo_total_carrera = 0.0

    def limpiar_pantalla(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _actualizar_tramo(self):
        """Calcula y acumula el coste del tramo actual antes de cambiar de estado o finalizar."""
        if self.tiempo_inicio_tramo is not None:
            ahora = time.time()
            duracion_tramo = ahora - self.tiempo_inicio_tramo
            tarifa = TARIFAS[self.estado_actual]
            self.coste_acumulado += duracion_tramo * tarifa
            self.tiempo_total_carrera += duracion_tramo
            self.tiempo_inicio_tramo = ahora

    def iniciar_carrera(self):
        self.carrera_activa = True
        self.coste_acumulado = 0.0
        self.tiempo_total_carrera = 0.0
        self.estado_actual = "PARADO"
        self.tiempo_inicio_tramo = time.time()
        print("\n✅ Carrera iniciada. Estado inicial: PARADO (0.02 €/s)")

    def cambiar_estado(self, nuevo_estado):
        if not self.carrera_activa:
            print("⚠️ No hay ninguna carrera activa.")
            return
        
        if self.estado_actual == nuevo_estado:
            print(f"ℹ️ El vehículo ya está en estado: {nuevo_estado}")
            return

        # Acumular tiempo y coste del estado anterior
        self._actualizar_tramo()
        
        # Cambiar al nuevo estado
        self.estado_actual = nuevo_estado
        print(f"\n🔄 Estado cambiado a: {self.estado_actual} ({TARIFAS[self.estado_actual]} €/s)")

    def finalizar_carrera(self):
        if not self.carrera_activa:
            print("⚠️ No hay ninguna carrera activa.")
            return

        self._actualizar_tramo()
        self.carrera_activa = False
        
        # Registrar en el histórico (US-05)
        registro = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duracion_seg": round(self.tiempo_total_carrera, 1),
            "total_eur": round(self.coste_acumulado, 2)
        }

        self.gestor_caja.registrar_carrera(self.tiempo_total_carrera, self.coste_acumulado)

        print("\n" + "="*40)
        print("🏁 CARRERA FINALIZADA")
        print(f"⏱️ Tiempo total: {int(self.tiempo_total_carrera)} segundos")
        print(f"💶 TOTAL A COBRAR: {self.coste_acumulado:.2f} €")
        print("="*40 + "\n")

    def mostrar_instrucciones(self):
        print("============================================")
        print("       TAXIMETRO TAXITECH SOLUTIONS        ")
        print("============================================")
        print("Comandos disponibles:")
        print("  [1] ó 'iniciar'    -> Iniciar nueva carrera")
        print("  [p] ó 'parado'     -> Cambiar a estado PARADO (0.02 €/s)")
        print("  [m] ó 'movimiento' -> Cambiar a estado EN MOVIMIENTO (0.05 €/s)")
        print("  [f] ó 'fin'        -> Finalizar carrera y calcular total")
        print("  [h] ó 'historico'  -> Ver histórico de carreras y caja (US-05)")
        print("  [s] ó 'salir'      -> Salir de la aplicación")
        print("============================================\n")

    def ejecutar(self):
        self.limpiar_pantalla()
        self.mostrar_instrucciones()

        while True:
            # Mostrar indicador dinámico si la carrera está en curso
            if self.carrera_activa:
                self._actualizar_tramo()
                prompt = f"[CARRERA ACTIVA | Estado: {self.estado_actual} | Acumulado: {self.coste_acumulado:.2f} €] > "
            else:
                prompt = "[ESPERA | Sin carrera activa] > "

            comando = input(prompt).strip().lower()

            if comando in ['1', 'iniciar']:
                if self.carrera_activa:
                    print("⚠️ Ya hay una carrera en curso. Finalízala antes de iniciar otra.")
                else:
                    self.iniciar_carrera()

            elif comando in ['p', 'parado']:
                self.cambiar_estado("PARADO")

            elif comando in ['m', 'movimiento']:
                self.cambiar_estado("MOVIMIENTO")

            elif comando in ['f', 'fin']:
                self.finalizar_carrera()

            elif comando in ['h', 'historico']:
                self.gestor_caja.mostrar_historico_y_caja(self.limpiar_pantalla)
                input("\nPresiona Enter para continuar...")

            elif comando in ['s', 'salir']:
                if self.carrera_activa:
                    confirmacion = input("⚠️ Hay una carrera en curso. ¿Seguro que deseas salir? (s/n): ")
                    if confirmacion.lower() != 's':
                        continue
                print("Gracias por usar TaxiTech Solutions. ¡Buen turno!")
                break
            else:
                print("❌ Comando no reconocido. Revisa las instrucciones:")
                self.mostrar_instrucciones()