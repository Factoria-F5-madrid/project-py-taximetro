import time
# importo aqui el modulo para medir el tiempo

class Taxi:

    #constructor

    def __init__(self):
        self.carrera_activa = False
        self.en_movimiento = False
        self.tiempo_inicio = 0.0
        self.ultimo_tiempo = 0.0
        self.importe_total = 0.0

    def iniciar_carrera(self):
        #aqui compruebo si ya existe alguna carrera
        if self.carrera_activa:
            print("Ya hay una carrera activa")    
            return

        tiempo_actual = time.monotonic()
        self.carrera_activa = True
        self.en_movimiento = False
        self.tiempo_inicio = tiempo_actual
        self.ultimo_tiempo = tiempo_actual
        self.importe_total = 0.0
        
        print("\nCarrera iniciada.")
        print("Estado: PARADO")
        print("Importe: 0.00 €")    


