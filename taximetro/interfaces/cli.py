import time

from taximetro import historial
from taximetro.carrera import Carrera
from taximetro.tarifas import ESTADO_MOVIMIENTO, ESTADO_PARADO


def mostrar_instrucciones() -> None:
    print("=== TAXIMETRO DIGITAL ===")
    print("Comandos:")
    print("  i -> iniciar una carrera")
    print("  p -> pasar a parado")
    print("  m -> pasar a movimiento")
    print("  f -> finalizar la carrera")
    print("  h -> ver las carreras de hoy")
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
    ahora = time.time()
    total = carrera.finalizar(ahora)
    historial.guardar_carrera(carrera.hora_inicio, ahora - carrera.hora_inicio, total)
    print(f"Total a cobrar: {total:.2f} €")


def mostrar_historial() -> None:
    carreras = historial.leer_carreras_de_hoy()
    if len(carreras) == 0:
        print("Hoy no hay carreras.")
    else:
        for fecha, duracion, importe in carreras:
            print(f"{fecha} | {duracion} s | {importe} €")


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

        elif comando == "h":
            mostrar_historial()

        elif comando == "s":
            print("Hasta luego.")
            break

        else:
            print("Comando no reconocido. Escribe i, p, m, f, h o s.")
