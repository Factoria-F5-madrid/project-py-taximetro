
"""Taxímetro digital de TaxiTech Solutions.

Incluye el MVP de la Fase 1 y las funcionalidades de la Fase 2:
historial diario, registro de eventos y configuración externa.
"""

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from time import monotonic


TARIFA_PARADO = 0.02
TARIFA_MOVIMIENTO = 0.05

DIRECTORIO_PROYECTO = Path(__file__).resolve().parent
DIRECTORIO_DATOS = DIRECTORIO_PROYECTO / "data"
ARCHIVO_HISTORIAL = DIRECTORIO_DATOS / "historial.json"
ARCHIVO_CONFIG = DIRECTORIO_PROYECTO / "config.json"

DIRECTORIO_LOGS = DIRECTORIO_PROYECTO / "logs"
ARCHIVO_LOG = DIRECTORIO_LOGS / "taximetro.log"

logger = logging.getLogger(__name__)


def configurar_logging() -> None:
    """Configura el registro estructurado de eventos en formato JSON."""
    DIRECTORIO_LOGS.mkdir(parents=True, exist_ok=True)

    class FormatoJSON(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            evento = {
                "fecha": self.formatTime(
                    record, "%Y-%m-%d %H:%M:%S"
                ),
                "nivel": record.levelname,
                "evento": record.getMessage(),
            }
            return json.dumps(evento, ensure_ascii=False)

    manejador = logging.FileHandler(
        ARCHIVO_LOG,
        encoding="utf-8",
    )
    manejador.setFormatter(FormatoJSON())

    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(manejador)
    logger.propagate = False

def cargar_tarifas(archivo: Path = ARCHIVO_CONFIG) -> tuple[float, float]:
    """Carga las tarifas desde JSON o utiliza los valores predeterminados."""
    try:
        with archivo.open("r", encoding="utf-8") as fichero:
            configuracion = json.load(fichero)

        tarifa_parado = configuracion["tarifa_parado"]
        tarifa_movimiento = configuracion["tarifa_movimiento"]

        tarifas = (tarifa_parado, tarifa_movimiento)

        for tarifa in tarifas:
            if (
                isinstance(tarifa, bool)
                or not isinstance(tarifa, (int, float))
                or not math.isfinite(tarifa)
                or tarifa < 0
            ):
                raise ValueError("Las tarifas deben ser no negativas.")

        logger.info(
            "Tarifas cargadas: parado=%.3f, movimiento=%.3f",
            tarifa_parado,
            tarifa_movimiento,
        )

        return float(tarifa_parado), float(tarifa_movimiento)

    except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError):
        logger.exception(
            "No se pudo cargar la configuracion. "
            "Se usaran las tarifas predeterminadas."
        )
        return TARIFA_PARADO, TARIFA_MOVIMIENTO


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


def guardar_carrera(
    carrera: Carrera,
    archivo: Path = ARCHIVO_HISTORIAL,
) -> None:
    """Añade una carrera finalizada al historial persistente."""
    try:
        archivo.parent.mkdir(parents=True, exist_ok=True)

        if archivo.exists():
            with archivo.open("r", encoding="utf-8") as fichero:
                historial = json.load(fichero)
        else:
            historial = []

        historial.append(carrera.obtener_registro())

        with archivo.open("w", encoding="utf-8") as fichero:
            json.dump(historial, fichero, ensure_ascii=False, indent=4)

        logger.info("Carrera guardada en el historial: %s", archivo)

    except (OSError, json.JSONDecodeError):
        logger.exception("Error al guardar la carrera en el historial")
        raise


def mostrar_historial() -> None:
    """Muestra las carreras realizadas durante el día actual."""
    if not ARCHIVO_HISTORIAL.exists():
        print("Todavía no hay carreras registradas hoy.")
        return

    try:
        with ARCHIVO_HISTORIAL.open("r", encoding="utf-8") as fichero:
            historial = json.load(fichero)

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

    except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError):
        logger.exception("Error al consultar el historial")
        print("No se pudo consultar el historial.")


def mostrar_ayuda() -> None:
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
    configurar_logging()
    logger.info("Programa iniciado")

    tarifa_parado, tarifa_movimiento = cargar_tarifas()

    print("TaxiTech Solutions - Taxímetro digital")
    print(
        f"Tarifas: parado {tarifa_parado:.3f} €/s | "
        f"movimiento {tarifa_movimiento:.3f} €/s"
    )
    mostrar_ayuda()

    carrera: Carrera | None = None

    while True:
        try:
            comando = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            logger.info("Programa interrumpido por el usuario")
            print("\nHasta luego.")
            return

        if comando == "iniciar":
            if carrera is not None:
                logger.warning("Intento de iniciar una carrera con otra activa")
                print("Ya hay una carrera activa.")
                continue

            carrera = Carrera(
                inicio=monotonic(),
                tarifa_parado=tarifa_parado,
                tarifa_movimiento=tarifa_movimiento,
            )
            logger.info("Carrera iniciada")
            print("Carrera iniciada. Estado inicial: parado.")

        elif comando in {"mover", "parar"}:
            if carrera is None:
                logger.warning("Intento de cambiar estado sin carrera activa")
                print("Primero debes iniciar una carrera.")
                continue

            estado = "movimiento" if comando == "mover" else "parado"
            carrera.cambiar_estado(estado)
            print(f"Estado actualizado: {estado}.")

        elif comando == "finalizar":
            if carrera is None:
                logger.warning("Intento de finalizar sin carrera activa")
                print("No hay ninguna carrera activa.")
                continue

            importe = carrera.finalizar()
            print(f"Total de la carrera: {importe:.2f} €")

            try:
                guardar_carrera(carrera)
                print("Carrera guardada en el historial.")
            except (OSError, json.JSONDecodeError) as error:
                print(f"Error al guardar el historial: {error}")

            carrera = None

        elif comando == "historial":
            mostrar_historial()

        elif comando == "ayuda":
            mostrar_ayuda()
        elif comando == "historial":
            mostrar_historial()
        elif comando == "salir":
            if carrera is not None:
                logger.warning("Intento de salir con una carrera activa")
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
            print("Comando no reconocido. Escribe 'ayuda' para ver las opciones.")


if __name__ == "__main__":
    ejecutar()
