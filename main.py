
"""Punto de entrada de TAXITECH NEO//DRIVE."""

import sys


def main() -> None:
    """Inicia la interfaz seleccionada."""

    if len(sys.argv) > 1 and sys.argv[1] == "--consola":
        from interfaces.consola import ejecutar
        ejecutar()
    else:
        from interfaces.grafica import ejecutar_grafica
        ejecutar_grafica()


if __name__ == "__main__":
    main()
