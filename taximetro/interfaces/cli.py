import time

from taximetro.carrera import Carrera


def mostrar_instrucciones() -> None:
    print("=== TAXIMETRO DIGITAL ===")
    print("Comandos:")
    print("  i -> iniciar una carrera")
    print("  s -> salir del programa")


def pedir_comando() -> str:
    return input("> ").strip().lower()


def iniciar_carrera() -> Carrera:
    carrera = Carrera(time.time())
    print("Carrera iniciada.")
    return carrera


def ejecutar() -> None:
    mostrar_instrucciones()

    while True:
        comando = pedir_comando()

        if comando == "i":
            iniciar_carrera()
            break

        if comando == "s":
            print("Hasta luego.")
            break

        print("Comando no reconocido. Escribe i o s.")
