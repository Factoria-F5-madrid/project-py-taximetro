import time
import os
from datetime import datetime
from app.historico import GestorHistorico
from app.registro import registrar_evento, registrar_error
from app.configuracion import GestorConfiguracion


class TaximetroMVP:
    def __init__(self):
        self.gestor_caja = GestorHistorico()  # Preparación para US-05
        self.carrera_activa = False
        self.estado_actual = "PARADO"  # "PARADO" o "MOVIMIENTO"
        self.tiempo_inicio_tramo = None
        self.coste_acumulado = 0.0
        self.tiempo_total_carrera = 0.0

        # Delegamos la responsabilidad de la configuración (Principio SOLID - SRP)
        config = GestorConfiguracion().cargar_tarifas()
        self.TARIFA_PARADO = config.get("TARIFA_PARADO", 0.02)
        self.TARIFA_MOVIMIENTO = config.get("TARIFA_MOVIMIENTO", 0.05)

    def limpiar_pantalla(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _actualizar_tramo(self):
        """Calcula y acumula el coste del tramo actual antes de cambiar de estado o finalizar."""
        if not self.carrera_activa or not self.tiempo_inicio_tramo:
            return

        ahora = datetime.now()
        duracion_tramo = (ahora - self.tiempo_inicio_tramo).total_seconds()
        self.tiempo_inicio_tramo = ahora

        self.tiempo_total_carrera += duracion_tramo

        if self.estado_actual == "PARADO":
            self.coste_acumulado += duracion_tramo * self.TARIFA_PARADO
        elif self.estado_actual == "MOVIMIENTO":
            self.coste_acumulado += duracion_tramo * self.TARIFA_MOVIMIENTO

    def mostrar_instrucciones(self):
        print("=" * 40)
        print("    TAXIMETRO TAXITECH SOLUTIONS")
        print("=" * 40)
        print("Comandos disponibles:")
        print("  [1] 'iniciar'    -> Iniciar nueva carrera")
        print(f"  [p] 'parado'     -> Cambiar a estado PARADO ({self.TARIFA_PARADO:.2f} euros/s)")
        print(f"  [m] 'movimiento' -> Cambiar a estado EN MOVIMIENTO ({self.TARIFA_MOVIMIENTO:.2f} euros/s)")
        print("  [f] 'fin'        -> Finalizar carrera y calcular total")
        print("  [h] 'historico'  -> Ver historico de carreras y caja (US-05)")
        print("  [s] 'salir'      -> Salir de la aplicacion")
        print("=" * 40 + "\n")

    def iniciar_carrera(self):
        self.carrera_activa = True
        self.estado_actual = "PARADO"
        self.tiempo_total_carrera = 0.0
        self.coste_acumulado = 0.0
        self.tiempo_inicio_tramo = datetime.now()
        registrar_evento("Nueva carrera iniciada.")
        print("\n🟢 Carrera iniciada en estado PARADO.")

    def cambiar_estado(self, nuevo_estado):
        if not self.carrera_activa:
            print("⚠️ No hay ninguna carrera activa para cambiar de estado.")
            return

        self._actualizar_tramo()
        self.estado_actual = nuevo_estado
        registrar_evento(f"Estado del vehículo cambiado a: {self.estado_actual}")
        print(f"\n🧭 Estado cambiado a: {self.estado_actual}")

    def finalizar_carrera(self):
        if not self.carrera_activa:
            print("⚠️ No hay ninguna carrera activa.")
            return

        self._actualizar_tramo()
        self.carrera_activa = False

        duracion_seg = round(self.tiempo_total_carrera, 1)
        total_eur = round(self.coste_acumulado, 2)

        self.gestor_caja.registrar_carrera(self.tiempo_total_carrera, self.coste_acumulado)
        registrar_evento(f"Carrera finalizada con éxito. Duración: {duracion_seg}s, Importe: {total_eur}€")

        print("\n" + "=" * 40)
        print("🏁 CARRERA FINALIZADA")
        print(f"⏱️ Tiempo total: {int(self.tiempo_total_carrera)} segundos")
        print(f"💰 TOTAL A COBRAR: {self.coste_acumulado:.2f} €")
        print("=" * 40 + "\n")

    def ejecutar(self):
        registrar_evento("Aplicación de taxímetro iniciada.")
        self.limpiar_pantalla()
        self.mostrar_instrucciones()

        try:
            while True:
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

                elif comando == 'error':
                    raise ZeroDivisionError("Prueba manual de error crítico de sistema.")

                else:
                    print("❌ Comando no reconocido. Revisa las instrucciones:")
                    self.mostrar_instrucciones()

        except Exception as e:
            registrar_error(f"Se ha producido un error crítico en la aplicación: {e}")
            raise