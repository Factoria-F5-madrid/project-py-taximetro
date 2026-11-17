
import json
import logging
import math
from pathlib import Path


logger = logging.getLogger(__name__)

TARIFA_PARADO = 0.02
TARIFA_MOVIMIENTO = 0.05

DIRECTORIO_PROYECTO = Path(__file__).resolve().parent.parent
ARCHIVO_CONFIG = DIRECTORIO_PROYECTO / "config.json"


def cargar_tarifas(
    archivo: Path = ARCHIVO_CONFIG,
) -> tuple[float, float]:
    """Carga las tarifas desde JSON o utiliza valores predeterminados."""
    try:
        with archivo.open("r", encoding="utf-8") as fichero:
            configuracion = json.load(fichero)

        tarifa_parado = configuracion["tarifa_parado"]
        tarifa_movimiento = configuracion["tarifa_movimiento"]

        for tarifa in (tarifa_parado, tarifa_movimiento):
            if (
                isinstance(tarifa, bool)
                or not isinstance(tarifa, (int, float))
                or not math.isfinite(tarifa)
                or tarifa < 0
            ):
                raise ValueError(
                    "Las tarifas deben ser números finitos no negativos."
                )

        logger.info(
            "Tarifas cargadas: parado=%.3f, movimiento=%.3f",
            tarifa_parado,
            tarifa_movimiento,
        )

        return float(tarifa_parado), float(tarifa_movimiento)

    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        ValueError,
        TypeError,
    ):
        logger.exception(
            "No se pudo cargar la configuración. "
            "Se utilizarán las tarifas predeterminadas."
        )
        return TARIFA_PARADO, TARIFA_MOVIMIENTO
