import time
# importo aqui el modulo para medir el tiempo

# Importamos las tarifas desde el archivo tarifas.py
from tarifas import TARIFA_PARADO, TARIFA_MOVIMIENTO

class Taxi:

    #constructor

    def __init__(self):
        self.carrera_activa = False
        self.en_movimiento = False
        self.tiempo_inicio = 0.0
        self.ultimo_tiempo = 0.0
        self.importe_total = 0.0
        self.numero_carrera = 0


    
    # US-01 y US-04: Iniciar una nueva carrera
    def iniciar_carrera(self):
        # Comprobamos si ya hay una carrera activa
        if self.carrera_activa:
            print("Ya hay una carrera activa.")
            return
        # Registramos el momento en que comienza
        tiempo_actual = time.monotonic()
        # Activamos la nueva carrera
        self.carrera_activa = True
        # El taxi empieza parado
        self.en_movimiento = False
        # Guardamos el nuevo instante de inicio
        self.tiempo_inicio = tiempo_actual
        # Reiniciamos el momento del último cálculo
        self.ultimo_tiempo = tiempo_actual
        # US-04: Reiniciamos el precio para la nueva carrera
        self.importe_total = 0.0
        # US-04: Sumamos una carrera al contador
        self.numero_carrera += 1
        # Informamos al taxista
        print("\nCarrera iniciada.")
        print(f"Número de carrera: {self.numero_carrera}")
        print("Estado: PARADO")
        print("Importe: 0.00 €")
   

    
    # US-02: Calcular el importe acumulado
    def calcular_importe(self):

        # Comprobamos que existe una carrera
        if not self.carrera_activa:
            return

        # Obtenemos el tiempo actual
        tiempo_actual = time.monotonic()

        # Calculamos los segundos desde el último cálculo
        segundos = tiempo_actual - self.ultimo_tiempo

        # Seleccionamos la tarifa según el estado
        if self.en_movimiento:
            tarifa = TARIFA_MOVIMIENTO
        else:
            tarifa = TARIFA_PARADO

        # Calculamos cuánto cuesta este tramo
        importe_tramo = segundos * tarifa

        # Sumamos el importe al total de la carrera
        self.importe_total += importe_tramo

        # Actualizamos el instante del último cálculo
        self.ultimo_tiempo = tiempo_actual


    
    # US-02: Indicar que el taxi empieza a moverse
    def iniciar_movimiento(self):

        # No podemos mover el taxi sin iniciar carrera
        if not self.carrera_activa:
            print("Primero debes iniciar una carrera.")
            return

        # Comprobamos si ya está en movimiento
        if self.en_movimiento:
            print("El taxi ya está en movimiento.")
            return

        # Calculamos el dinero acumulado estando parado
        self.calcular_importe()

        # Cambiamos el estado del taxi
        self.en_movimiento = True

        print("\nEl taxi está EN MOVIMIENTO.")



    # US-02: Indicar que el taxi se detiene
    def detener_movimiento(self):

        # Comprobamos que hay una carrera activa
        if not self.carrera_activa:
            print("Primero debes iniciar una carrera.")
            return

        # Comprobamos si ya está parado
        if not self.en_movimiento:
            print("El taxi ya está parado.")
            return

        # Calculamos el tiempo que estuvo en movimiento
        self.calcular_importe()

        # Cambiamos el estado a parado
        self.en_movimiento = False

        print("\nEl taxi está PARADO.")


    # US-02: Consultar el importe actual
    def consultar_importe(self):

        # No podemos consultar una carrera inexistente
        if not self.carrera_activa:
            print("No hay ninguna carrera activa.")
            return

        # Actualizamos el importe hasta este momento
        self.calcular_importe()

        # Comprobamos el estado actual del taxi
        if self.en_movimiento:
            estado = "EN MOVIMIENTO"
        else:
            estado = "PARADO"

        # Mostramos la información
        print("\nEstado:", estado)
        print(f"Importe actual: {self.importe_total:.2f} €")


    # US-03: Finalizar la carrera
    def finalizar_carrera(self):

        # 1. Comprobamos si existe una carrera activa
        if not self.carrera_activa:
            print("No hay ninguna carrera activa.")
            return

        # 2. Calculamos el importe del último tramo
        # antes de finalizar la carrera
        self.calcular_importe()

        # 3. Calculamos la duración total en segundos
        duracion = self.ultimo_tiempo - self.tiempo_inicio

        # 4. Marcamos la carrera como finalizada
        self.carrera_activa = False

        # 5. Dejamos el taxi en estado parado
        self.en_movimiento = False

        # 6. Mostramos el resumen al conductor
        print("\n=============================")
        print("      CARRERA FINALIZADA")
        print("=============================")

        # US-04: Identificar qué carrera ha terminado
        print(f"Número de carrera: {self.numero_carrera}")


        # Mostramos la duración con dos decimales
        print(f"Duración: {duracion:.2f} segundos")

        # Mostramos el importe total en euros
        print(f"Importe total: {self.importe_total:.2f} €")

        print("=============================")
