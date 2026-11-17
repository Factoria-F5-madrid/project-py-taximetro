
import logging
from dataclasses import dataclass, field
from datetime import datetime
from time import monotonic


logger = logging.getLogger(__name__)

TARIFA_PARADO = 0.02
TARIFA_MOVIMIENTO = 0.05


@dataclass
class Carrera:
    """Estado, duración y acumulación de una carrera activa."""

    inicio: float
    estado: str = "parado"
    ultimo_cambio: float | None = None
    importe: float = 0.0
    fecha_inicio: str = field(
        default_factory=lambda: datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
    )
    duracion_segundos: float = 0.0
    tarifa_parado: float = TARIFA_PARADO
    tarifa_movimiento: float = TARIFA_MOVIMIENTO

    def __post_init__(self) -> None:
        self.ultimo_cambio = self.inicio

    def actualizar(self, ahora: float | None = None) -> None:
        """Acumula el tiempo con la tarifa del estado actual."""
        ahora = monotonic() if ahora is None else ahora
        assert self.ultimo_cambio is not None

        segundos = max(0.0, ahora - self.ultimo_cambio)

        tarifa = (
            self.tarifa_movimiento
            if self.estado == "movimiento"
            else self.tarifa_parado
        )

        self.importe += segundos * tarifa
        self.ultimo_cambio = ahora

    def cambiar_estado(self, estado: str, ahora: float | None = None) -> None:
        """Cambia el estado después de cerrar el tramo anterior."""
        if estado not in {"parado", "movimiento"}:
            raise ValueError("El estado debe ser 'parado' o 'movimiento'.")

        self.actualizar(ahora)

        estado_anterior = self.estado
        self.estado = estado

        logger.info("Cambio de estado: %s -> %s", estado_anterior, estado)

    def finalizar(self, ahora: float | None = None) -> float:
        """Cierra la carrera y devuelve el importe final."""
        ahora = monotonic() if ahora is None else ahora

        self.actualizar(ahora)
        self.duracion_segundos = max(0.0, ahora - self.inicio)

        logger.info(
            "Carrera finalizada: duracion=%.2f segundos, importe=%.2f euros",
            self.duracion_segundos,
            self.importe,
        )

        return self.importe

    def obtener_registro(self) -> dict:
        """Prepara los datos de la carrera para guardarlos."""
        return {
            "fecha_inicio": self.fecha_inicio,
            "duracion_segundos": round(self.duracion_segundos, 2),
            "importe_euros": round(self.importe, 2),
        }
