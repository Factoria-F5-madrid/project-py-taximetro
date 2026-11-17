
"""Configuración del sistema de logging de TaxiTech Solutions."""

import json
import logging
from pathlib import Path


DIRECTORIO_PROYECTO = Path(__file__).resolve().parent.parent
DIRECTORIO_LOGS = DIRECTORIO_PROYECTO / "logs"
ARCHIVO_LOG = DIRECTORIO_LOGS / "taximetro.log"

logger = logging.getLogger("taximetro")


class FormatoJSON(logging.Formatter):
    """Convierte cada evento de logging en una línea JSON."""

    def format(self, record: logging.LogRecord) -> str:
        evento = {
            "fecha": self.formatTime(
                record,
                "%Y-%m-%d %H:%M:%S",
            ),
            "nivel": record.levelname,
            "evento": record.getMessage(),
        }

        if record.exc_info:
            evento["error"] = self.formatException(record.exc_info)

        return json.dumps(evento, ensure_ascii=False)


def configurar_logging() -> None:
    """Configura el registro estructurado de eventos en JSON."""
    DIRECTORIO_LOGS.mkdir(parents=True, exist_ok=True)

    manejador = logging.FileHandler(
        ARCHIVO_LOG,
        encoding="utf-8",
    )

    manejador.setFormatter(FormatoJSON())

    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(manejador)
    logger.propagate = False
