
"""Compatibilidad con el antiguo punto de entrada de TaxiTech Solutions.

La lógica de negocio está en taximetro/.
La interfaz de consola está en interfaces/consola.py.
El nuevo punto de entrada es main.py.
"""

# Compatibilidad con los imports utilizados por los tests
from taximetro.carrera import Carrera
from taximetro.taximetro import Taximetro

from taximetro.configuracion import (
    cargar_tarifas,
    TARIFA_PARADO,
    TARIFA_MOVIMIENTO,
)

from taximetro.persistencia import (
    guardar_carrera,
    cargar_historial,
    ARCHIVO_HISTORIAL,
)

from taximetro.logging_config import configurar_logging

from interfaces.consola import (
    mostrar_historial,
    mostrar_ayuda,
    ejecutar,
)


if __name__ == "__main__":
    ejecutar()
