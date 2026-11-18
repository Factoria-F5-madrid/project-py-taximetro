import logging
import os

# Asegurar que el directorio de logs dentro de app existe
os.makedirs("app/logs", exist_ok=True)

ruta_log = "app/logs/taximetro.log"

# Configurar el logger explícitamente para garantizar la creación del archivo
logger = logging.getLogger("TaximetroAuditoria")
logger.setLevel(logging.INFO)

if not logger.handlers:
    # Manejador de archivo
    file_handler = logging.FileHandler(ruta_log, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def registrar_evento(mensaje):
    logger.info(mensaje)

def registrar_error(mensaje):
    logger.error(mensaje)