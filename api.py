
"""API REST de TAXITECH NEO//DRIVE."""

import logging
import secrets
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from taximetro.taximetro import Taximetro
from taximetro.configuracion import cargar_tarifas
from taximetro.autenticacion import (
    verificar_contrasena,
    credenciales_configuradas,
    ErrorAutenticacion,
)
from taximetro.persistencia_sqlite import (
    inicializar_bd,
    migrar_historial_json,
    guardar_carrera,
    cargar_historial,
)
from taximetro.logging_config import configurar_logging


# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

logger = logging.getLogger("taximetro")

BASE_DIR = Path(__file__).resolve().parent

seguridad = HTTPBasic()
bloqueo = threading.RLock()

motor = None
carrera_pendiente = None


# --------------------------------------------------
# MODELOS
# --------------------------------------------------

class CambioEstado(BaseModel):
    estado: Literal["parado", "movimiento"]


# --------------------------------------------------
# INICIALIZACIÓN
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global motor

    configurar_logging()
    inicializar_bd()

    migrados = migrar_historial_json()

    logger.info(
        "Migración inicial completada: %s registros",
        migrados,
    )

    tarifa_parado, tarifa_movimiento = cargar_tarifas()

    motor = Taximetro(
        tarifa_parado=tarifa_parado,
        tarifa_movimiento=tarifa_movimiento,
    )

    logger.info("TAXITECH iniciado correctamente.")

    yield

    logger.info("TAXITECH detenido.")


app = FastAPI(
    title="TAXITECH NEO//DRIVE",
    description="API REST para gestión de taxímetro e historial.",
    version="1.0.0",
    lifespan=lifespan,
)


# --------------------------------------------------
# AUTENTICACIÓN
# --------------------------------------------------

def autenticar_api(
    credentials: HTTPBasicCredentials = Depends(seguridad),
):
    if not credenciales_configuradas():
        raise HTTPException(
            status_code=503,
            detail="No hay credenciales configuradas.",
        )

    usuario_valido = secrets.compare_digest(
        credentials.username,
        "taxitech",
    )

    try:
        contrasena_valida = verificar_contrasena(
            credentials.password
        )
    except ErrorAutenticacion:
        raise HTTPException(
            status_code=503,
            detail="No se pueden verificar las credenciales.",
        )

    if not usuario_valido or not contrasena_valida:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


# --------------------------------------------------
# SERVICIO
# --------------------------------------------------

def obtener_motor():
    if motor is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio todavía no está inicializado.",
        )

    return motor


# --------------------------------------------------
# PANEL WEB DE ADMINISTRACIÓN
# --------------------------------------------------

@app.get("/admin")
def panel_administracion():
    archivo = BASE_DIR / "templates" / "admin.html"

    if not archivo.is_file():
        raise HTTPException(
            status_code=404,
            detail="No se encuentra el panel de administración.",
        )

    return FileResponse(archivo)


# --------------------------------------------------
# COMPROBACIÓN DEL SERVICIO
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "TAXITECH",
    }


# --------------------------------------------------
# INICIAR CARRERA
# --------------------------------------------------

@app.post(
    "/api/carreras",
    dependencies=[Depends(autenticar_api)],
)
def iniciar_carrera():
    with bloqueo:
        servicio = obtener_motor()

        try:
            carrera = servicio.iniciar_carrera()

            return {
                "mensaje": "Carrera iniciada.",
                "fecha_inicio": carrera.fecha_inicio,
                "estado": carrera.estado,
            }

        except RuntimeError as error:
            raise HTTPException(
                status_code=409,
                detail=str(error),
            )


# --------------------------------------------------
# CAMBIAR ESTADO
# --------------------------------------------------

@app.patch(
    "/api/carreras/estado",
    dependencies=[Depends(autenticar_api)],
)
def cambiar_estado(datos: CambioEstado):
    with bloqueo:
        servicio = obtener_motor()

        try:
            servicio.cambiar_estado(datos.estado)

            return {
                "mensaje": "Estado actualizado.",
                "estado": datos.estado,
            }

        except RuntimeError as error:
            raise HTTPException(
                status_code=409,
                detail=str(error),
            )

        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            )


# --------------------------------------------------
# FINALIZAR CARRERA
# --------------------------------------------------

@app.post(
    "/api/carreras/finalizar",
    dependencies=[Depends(autenticar_api)],
)
def finalizar_carrera():
    global carrera_pendiente

    with bloqueo:
        servicio = obtener_motor()

        if carrera_pendiente is None:
            try:
                carrera_pendiente = servicio.finalizar_carrera()

            except RuntimeError as error:
                raise HTTPException(
                    status_code=409,
                    detail=str(error),
                )

        try:
            registro = carrera_pendiente.obtener_registro()

            identificador = guardar_carrera(
                carrera_pendiente
            )

            carrera_pendiente = None

            return {
                "mensaje": "Carrera finalizada y guardada.",
                "id": identificador,
                **registro,
            }

        except (OSError, ValueError) as error:
            logger.exception(
                "Error al guardar carrera en SQLite."
            )

            raise HTTPException(
                status_code=503,
                detail=(
                    "Carrera finalizada, pero pendiente de guardar. "
                    "Puedes reintentar la operación."
                ),
            ) from error


# --------------------------------------------------
# CONSULTAR HISTORIAL
# --------------------------------------------------

@app.get(
    "/api/carreras",
    dependencies=[Depends(autenticar_api)],
)
def consultar_historial():
    try:
        carreras = cargar_historial()

        return {
            "total": len(carreras),
            "carreras": carreras,
        }

    except (OSError, ValueError) as error:
        logger.exception(
            "Error consultando historial."
        )

        raise HTTPException(
            status_code=500,
            detail="No se pudo consultar el historial.",
        ) from error
