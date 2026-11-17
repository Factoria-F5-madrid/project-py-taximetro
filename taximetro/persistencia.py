
"""Persistencia de las carreras de TaxiTech Solutions."""

import json
import logging
from pathlib import Path

from taximetro.carrera import Carrera


logger = logging.getLogger("taximetro")

DIRECTORIO_PROYECTO = Path(__file__).resolve().parent.parent
DIRECTORIO_DATOS = DIRECTORIO_PROYECTO / "data"
ARCHIVO_HISTORIAL = DIRECTORIO_DATOS / "historial.json"


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

        if not isinstance(historial, list):
            raise ValueError("El historial debe contener una lista.")

        historial.append(carrera.obtener_registro())

        with archivo.open("w", encoding="utf-8") as fichero:
            json.dump(
                historial,
                fichero,
                ensure_ascii=False,
                indent=4,
            )

        logger.info(
            "Carrera guardada en el historial: %s",
            archivo,
        )

    except (OSError, json.JSONDecodeError, ValueError):
        logger.exception("Error al guardar la carrera en el historial.")
        raise


def cargar_historial(
    archivo: Path = ARCHIVO_HISTORIAL,
) -> list[dict]:
    """Recupera todas las carreras almacenadas."""
    if not archivo.exists():
        return []

    try:
        with archivo.open("r", encoding="utf-8") as fichero:
            historial = json.load(fichero)

        if not isinstance(historial, list):
            raise ValueError("El historial debe contener una lista.")

        return historial

    except (OSError, json.JSONDecodeError, ValueError):
        logger.exception("Error al cargar el historial.")
        raise
