
from time import monotonic

from taximetro.carrera import Carrera


class Taximetro:
    """Coordina el funcionamiento de las carreras."""

    def __init__(
        self,
        tarifa_parado: float = 0.02,
        tarifa_movimiento: float = 0.05,
    ) -> None:
        self.tarifa_parado = tarifa_parado
        self.tarifa_movimiento = tarifa_movimiento
        self.carrera_actual: Carrera | None = None

    def iniciar_carrera(self) -> Carrera:
        """Inicia una nueva carrera si no hay otra activa."""
        if self.carrera_actual is not None:
            raise RuntimeError("Ya hay una carrera activa.")

        self.carrera_actual = Carrera(
            inicio=monotonic(),
            tarifa_parado=self.tarifa_parado,
            tarifa_movimiento=self.tarifa_movimiento,
        )

        return self.carrera_actual

    def cambiar_estado(self, estado: str) -> None:
        """Cambia el estado de la carrera activa."""
        if self.carrera_actual is None:
            raise RuntimeError("No hay ninguna carrera activa.")

        self.carrera_actual.cambiar_estado(estado)

    def finalizar_carrera(self) -> Carrera:
        """Finaliza la carrera activa y devuelve su objeto."""
        if self.carrera_actual is None:
            raise RuntimeError("No hay ninguna carrera activa.")

        self.carrera_actual.finalizar()

        carrera_finalizada = self.carrera_actual
        self.carrera_actual = None

        return carrera_finalizada

    def hay_carrera_activa(self) -> bool:
        """Indica si existe una carrera en curso."""
        return self.carrera_actual is not None
