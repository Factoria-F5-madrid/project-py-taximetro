import time

from taximetro.carrera import Carrera
from taximetro.tarifas import ESTADO_MOVIMIENTO, ESTADO_PARADO

def mostrar_instrucciones() -> None:
    print("=== TAXIMETRO DIGITAL ===")
    print("Comandos:")
    print("  i -> iniciar una carrera")
    print("  p -> pasar a parado")
    print("  m -> pasar a movimiento")
    print("  f -> finalizar la carrera")
    print("  s -> salir del programa")

def pedir_comando() -> str:
    return input("> ").strip().lower()

def iniciar_carrera() -> Carrera:
    carrera = Carrera(time.time())
    print("Carrera iniciada.")
    return carrera

def cambiar_estado(carrera: Carrera, estado: str) -> None:
    carrera.cambiar_estado(estado, time.time())
    print("Estado: " + estado)

def finalizar_carrera(carrera: Carrera) -> None:
    total = carrera.finalizar(time.time())
    print(f"Total a cobrar: {total:.2f} €")

def ejecutar() -> None:
    mostrar_instrucciones()

    carrera = None

    while True:
        comando = pedir_comando()

        if comando == "i":
            if carrera is None:
                carrera = iniciar_carrera()
            else:
                print("Ya hay una carrera en curso.")

        elif comando == "p":
            if carrera is None:
                print("No hay ninguna carrera en curso.")
            else:
                cambiar_estado(carrera, ESTADO_PARADO)

        elif comando == "m":
            if carrera is None:
                print("No hay ninguna carrera en curso.")
            else:
                cambiar_estado(carrera, ESTADO_MOVIMIENTO)

        elif comando == "f":
            if carrera is None:
                print("No hay ninguna carrera en curso.")
            else:
                finalizar_carrera(carrera)
                carrera = None

        elif comando == "s":
            print("Hasta luego.")
            break

        else:
            print("Comando no reconocido. Escribe i, p, m, f o s.")
