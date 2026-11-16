import os
from datetime import datetime

CARPETA_DATOS = "data"
ARCHIVO_HISTORIAL = "data/historial.txt"
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"
FORMATO_DIA = "%Y-%m-%d"


def guardar_carrera(hora_inicio: float, duracion: float, importe: float) -> None:
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    fecha = datetime.fromtimestamp(hora_inicio).strftime(FORMATO_FECHA)
    with open(ARCHIVO_HISTORIAL, "a", encoding="utf-8") as archivo:
        archivo.write(f"{fecha};{duracion:.0f};{importe:.2f}\n")


def leer_carreras_de_hoy() -> list[list[str]]:
    carreras = []
    if not os.path.exists(ARCHIVO_HISTORIAL):
        return carreras
    hoy = datetime.now().strftime(FORMATO_DIA)
    with open(ARCHIVO_HISTORIAL, encoding="utf-8") as archivo:
        for linea in archivo:
            datos = linea.strip().split(";")
            if datos[0].startswith(hoy):
                carreras.append(datos)
    return carreras
