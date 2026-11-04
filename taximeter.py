"""Taxímetro digital de línea de comandos.

Implementa el MVP de la Fase 1: iniciar, cambiar el estado del taxi,
finalizar una carrera y comenzar otra sin cerrar el programa.
"""

from dataclasses import dataclass
from time import monotonic


TARIFA_PARADO = 0.02
TARIFA_MOVIMIENTO = 0.05


@dataclass
class Carrera:
    """Estado y acumulación de una carrera activa."""

    inicio: float
    estado: str = "parado"
    ultimo_cambio: float | None = None
    importe: float = 0.0

    def __post_init__(self) -> None:
        self.ultimo_cambio = self.inicio

    def actualizar(self, ahora: float | None = None) -> None:
        """Acumula el tiempo transcurrido con la tarifa del estado actual."""
        ahora = monotonic() if ahora is None else ahora
        assert self.ultimo_cambio is not None
        segundos = max(0.0, ahora - self.ultimo_cambio)
        tarifa = (
            TARIFA_MOVIMIENTO
            if self.estado == "movimiento"
            else TARIFA_PARADO
        )
        self.importe += segundos * tarifa
        self.ultimo_cambio = ahora

    def cambiar_estado(self, estado: str, ahora: float | None = None) -> None:
        """Cambia el estado después de cerrar el tramo anterior."""
        if estado not in {"parado", "movimiento"}:
            raise ValueError("El estado debe ser 'parado' o 'movimiento'.")
        self.actualizar(ahora)
        self.estado = estado

    def finalizar(self, ahora: float | None = None) -> float:
        """Cierra la carrera y devuelve el importe final."""
        self.actualizar(ahora)
        return self.importe


def mostrar_ayuda() -> None:
    print(
        "\nComandos:"
        "\n  iniciar      Comienza una carrera"
        "\n  mover        Cambia a tarifa de taxi en movimiento"
        "\n  parar        Cambia a tarifa de taxi parado"
        "\n  finalizar    Termina la carrera y muestra el importe"
        "\n  ayuda        Muestra esta ayuda"
        "\n  salir        Cierra el programa"
    )


def ejecutar() -> None:
    """Ejecuta el bucle interactivo del taxímetro."""
    carrera: Carrera | None = None

    print("TaxiTech Solutions — Taxímetro digital")
    mostrar_ayuda()

    while True:
        try:
            comando = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            return

        if comando == "iniciar":
            if carrera is not None:
                print("Ya hay una carrera activa.")
                continue
            carrera = Carrera(monotonic())
            print("Carrera iniciada. Estado inicial: parado.")
        elif comando in {"mover", "parar"}:
            if carrera is None:
                print("Primero debes iniciar una carrera.")
                continue
            estado = "movimiento" if comando == "mover" else "parado"
            carrera.cambiar_estado(estado)
            print(f"Estado actualizado: {estado}.")
        elif comando == "finalizar":
            if carrera is None:
                print("No hay ninguna carrera activa.")
                continue
            importe = carrera.finalizar()
            print(f"Total de la carrera: {importe:.2f} €")
            carrera = None
        elif comando == "ayuda":
            mostrar_ayuda()
        elif comando == "salir":
            if carrera is not None:
                print("No se puede salir con una carrera activa. Finalízala primero.")
                continue
            print("Hasta luego.")
            return
        elif comando:
            print("Comando no reconocido. Escribe 'ayuda' para ver las opciones.")


if __name__ == "__main__":
    ejecutar()
