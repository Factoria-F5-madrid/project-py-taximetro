
"""Interfaz de consola de TaxiTech Solutions."""

import json
import logging
from datetime import datetime

from taximetro.taximetro import Taximetro
from taximetro.configuracion import cargar_tarifas
from taximetro.persistencia import guardar_carrera, cargar_historial
from taximetro.logging_config import configurar_logging
from taximetro.autenticacion import autenticar_consola

logger = logging.getLogger("taximetro")


def mostrar_historial() -> None:
    """Muestra las carreras realizadas durante el día actual."""
    try:
        historial = cargar_historial()
        hoy = datetime.now().astimezone().date()

        carreras_hoy = [
            carrera
            for carrera in historial
            if datetime.fromisoformat(
                carrera["fecha_inicio"]
            ).astimezone().date() == hoy
        ]

        if not carreras_hoy:
            print("Todavía no hay carreras registradas hoy.")
            return

        total = 0.0
        print("\nHistorial de carreras de hoy:")

        for numero, carrera in enumerate(carreras_hoy, start=1):
            importe = carrera["importe_euros"]
            total += importe

            print(
                f"{numero}. {carrera['fecha_inicio']} | "
                f"{carrera['duracion_segundos']:.2f} segundos | "
                f"{importe:.2f} €"
            )

        print(f"Total recaudado: {total:.2f} €")

    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        ValueError,
        TypeError,
    ):
        logger.exception("Error al consultar el historial.")
        print("No se pudo consultar el historial.")


def mostrar_ayuda() -> None:
    """Muestra los comandos disponibles."""
    print(
        "\nComandos:"
        "\n  iniciar      Comienza una carrera"
        "\n  mover        Cambia a tarifa de taxi en movimiento"
        "\n  parar        Cambia a tarifa de taxi parado"
        "\n  finalizar    Termina la carrera y muestra el importe"
        "\n  historial    Muestra las carreras del día"
        "\n  ayuda        Muestra esta ayuda"
        "\n  salir        Cierra el programa"
    )


def ejecutar() -> None:
    """Ejecuta el bucle interactivo del taxímetro."""

    # Comprobar acceso antes de iniciar el programa.
    if not autenticar_consola():
        return

    configurar_logging()
    logger.info("Programa iniciado")

    tarifa_parado, tarifa_movimiento = cargar_tarifas()

    taximetro = Taximetro(
        tarifa_parado=tarifa_parado,
        tarifa_movimiento=tarifa_movimiento,
    )

    print("TaxiTech Solutions - Taxímetro digital")
    print(
        f"Tarifas: parado {tarifa_parado:.3f} €/s | "
        f"movimiento {tarifa_movimiento:.3f} €/s"
    )

    mostrar_ayuda()

    while True:
        try:
            comando = input("\n> ").strip().lower()

        except (EOFError, KeyboardInterrupt):
            if taximetro.hay_carrera_activa():
                logger.warning(
                    "Programa interrumpido con una carrera activa."
                )
                print(
                    "\nHay una carrera activa. "
                    "Finalízala antes de salir."
                )
                continue

            logger.info("Programa interrumpido por el usuario.")
            print("\nHasta luego.")
            return

        if comando == "iniciar":
            if taximetro.hay_carrera_activa():
                logger.warning(
                    "Intento de iniciar una carrera con otra activa."
                )
                print("Ya hay una carrera activa.")
                continue

            taximetro.iniciar_carrera()
            logger.info("Carrera iniciada")
            print("Carrera iniciada. Estado inicial: parado.")

        elif comando in {"mover", "parar"}:
            if not taximetro.hay_carrera_activa():
                logger.warning(
                    "Intento de cambiar estado sin carrera activa."
                )
                print("Primero debes iniciar una carrera.")
                continue

            estado = "movimiento" if comando == "mover" else "parado"
            taximetro.cambiar_estado(estado)
            print(f"Estado actualizado: {estado}.")

        elif comando == "finalizar":
            if not taximetro.hay_carrera_activa():
                logger.warning(
                    "Intento de finalizar sin carrera activa."
                )
                print("No hay ninguna carrera activa.")
                continue

            carrera = taximetro.finalizar_carrera()
            importe = carrera.importe

            print(f"Total de la carrera: {importe:.2f} €")

            try:
                guardar_carrera(carrera)
                print("Carrera guardada en el historial.")
            except (OSError, json.JSONDecodeError, ValueError) as error:
                logger.exception("Error al guardar la carrera.")
                print(f"Error al guardar el historial: {error}")

        elif comando == "historial":
            mostrar_historial()

        elif comando == "ayuda":
            mostrar_ayuda()

        elif comando == "salir":
            if taximetro.hay_carrera_activa():
                logger.warning(
                    "Intento de salir con una carrera activa."
                )
                print(
                    "No se puede salir con una carrera activa. "
                    "Finalízala primero."
                )
                continue

            logger.info("Programa finalizado")
            print("Hasta luego.")
            return

        elif comando:
            logger.warning("Comando no reconocido: %s", comando)
            print(
                "Comando no reconocido. "
                "Escribe 'ayuda' para ver las opciones."
            )
