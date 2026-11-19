import csv
# US-05: Histórico de carreras del taxímetro
# Importamos csv para guardar y leer archivos CSV
# Importamos datetime para registrar fechas y horas
from datetime import datetime

# Importamos Path para trabajar con rutas de archivos
from pathlib import Path


# Archivo donde guardaremos todas las carreras
# Se ubicará en la misma carpeta que historial.py
ARCHIVO_HISTORIAL = Path(__file__).with_name(
    "historial_carreras.csv"
)


# Nombres de las columnas que tendrá el CSV
COLUMNAS = [
    "fecha",
    "hora",
    "duracion_segundos",
    "importe_euros"
]


# US-05: Guardar una carrera finalizada
def guardar_carrera(duracion, importe):

    # Comprobamos si todavía no existe el archivo
    # o si existe, pero está vacío
    archivo_nuevo = (
        not ARCHIVO_HISTORIAL.exists()
        or ARCHIVO_HISTORIAL.stat().st_size == 0
    )

    # Obtenemos la fecha y hora actuales del sistema
    ahora = datetime.now()

    # Abrimos el archivo en modo "a" (añadir)
    # Si no existe, Python lo crea automáticamente
    with ARCHIVO_HISTORIAL.open(
        "a", newline="", encoding="utf-8"
    ) as archivo:

        # Creamos un escritor de archivos CSV
        escritor = csv.writer(archivo)

        # Escribimos la cabecera solo si es un archivo nuevo
        if archivo_nuevo:
            escritor.writerow(COLUMNAS)

        # Guardamos los datos de la carrera
        escritor.writerow([
            ahora.strftime("%Y-%m-%d"),
            ahora.strftime("%H:%M:%S"),
            f"{duracion:.2f}",
            f"{importe:.2f}"
        ])

    print("Carrera guardada en el histórico.")


# US-05: Mostrar las carreras realizadas hoy
def mostrar_historial_hoy():

    # Obtenemos la fecha actual del sistema
    hoy = datetime.now().strftime("%Y-%m-%d")

    # Si no existe el archivo, no tenemos historial
    if not ARCHIVO_HISTORIAL.exists():
        print("Todavía no hay carreras guardadas.")
        return

    # Variables para calcular el resumen del día
    numero_carreras = 0
    total_dia = 0.0

    print("\n=============================")
    print("   HISTÓRICO DE CARRERAS")
    print("=============================")
    print("Fecha:", hoy)

    # Abrimos el CSV para leer su contenido
    with ARCHIVO_HISTORIAL.open(
        "r", newline="", encoding="utf-8"
    ) as archivo:

        # DictReader permite acceder por nombre de columna
        lector = csv.DictReader(archivo)

        # Recorremos las carreras guardadas
        for carrera in lector:

            # Mostramos solo las carreras de hoy
            if carrera["fecha"] == hoy:

                # Contamos una carrera más
                numero_carreras += 1

                # Convertimos el importe a número decimal
                importe = float(carrera["importe_euros"])

                # Acumulamos el dinero recaudado
                total_dia += importe

                # Mostramos la carrera en pantalla
                print(
                    f"{numero_carreras}. "
                    f"Hora: {carrera['hora']} | "
                    f"Duración: {carrera['duracion_segundos']} s | "
                    f"Importe: {importe:.2f} €"
                )

    # Comprobamos si existen carreras del día
    if numero_carreras == 0:
        print("No hay carreras registradas hoy.")
        return

    # Mostramos el resumen del día
    print("-----------------------------")
    print(f"Carreras realizadas: {numero_carreras}")
    print(f"Total recaudado: {total_dia:.2f} €")
    print("=============================")
