
"""Persistencia relacional de TAXITECH mediante SQLite."""

import json
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger("taximetro")

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "taxitech.db"
JSON_PATH = BASE_DIR / "data" / "historial.json"


def conectar(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(db_path)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_bd(db_path: Path = DB_PATH) -> None:
    with conectar(db_path) as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS carreras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_inicio TEXT NOT NULL,
                duracion_segundos REAL NOT NULL,
                importe_euros REAL NOT NULL
            )
        """)

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS migraciones (
                nombre TEXT PRIMARY KEY,
                completada_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

    logger.info(
        "Base de datos SQLite inicializada: %s",
        db_path,
    )


def guardar_registro(
    registro: dict,
    db_path: Path = DB_PATH,
) -> int:
    campos = (
        "fecha_inicio",
        "duracion_segundos",
        "importe_euros",
    )

    if not isinstance(registro, dict) or any(
        campo not in registro for campo in campos
    ):
        raise ValueError("Registro de carrera incompleto.")

    with conectar(db_path) as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO carreras (
                fecha_inicio,
                duracion_segundos,
                importe_euros
            ) VALUES (?, ?, ?)
            """,
            tuple(registro[campo] for campo in campos),
        )

        return cursor.lastrowid


def guardar_carrera(
    carrera,
    db_path: Path = DB_PATH,
) -> int:
    return guardar_registro(
        carrera.obtener_registro(),
        db_path,
    )


def cargar_historial(
    db_path: Path = DB_PATH,
) -> list[dict]:
    with conectar(db_path) as conexion:
        filas = conexion.execute("""
            SELECT
                fecha_inicio,
                duracion_segundos,
                importe_euros
            FROM carreras
            ORDER BY id
        """).fetchall()

    return [dict(fila) for fila in filas]


def migrar_historial_json(
    json_path: Path = JSON_PATH,
    db_path: Path = DB_PATH,
) -> int:
    """
    Migra el historial JSON una sola vez.

    La identificación de la migración es independiente
    de la ruta del archivo y del sistema operativo.
    Conserva el JSON original.
    """

    if not json_path.exists():
        inicializar_bd(db_path)
        return 0

    historial = json.loads(
        json_path.read_text(encoding="utf-8")
    )

    if not isinstance(historial, list):
        raise ValueError(
            "El historial JSON debe contener una lista."
        )

    inicializar_bd(db_path)

    # Reconoce también la migración antigua registrada en Windows.
    nombre = "historial_json:v1"

    with conectar(db_path) as conexion:

        existente = conexion.execute(
            """
            SELECT 1
            FROM migraciones
            WHERE nombre = ?
               OR nombre LIKE 'historial_json:%'
            LIMIT 1
            """,
            (nombre,),
        ).fetchone()

        if existente:
            logger.info(
                "La migración del historial ya estaba completada."
            )
            return 0

        campos = (
            "fecha_inicio",
            "duracion_segundos",
            "importe_euros",
        )

        for registro in historial:

            if not isinstance(registro, dict) or any(
                campo not in registro for campo in campos
            ):
                raise ValueError(
                    "Registro JSON incompleto."
                )

            conexion.execute(
                """
                INSERT INTO carreras (
                    fecha_inicio,
                    duracion_segundos,
                    importe_euros
                ) VALUES (?, ?, ?)
                """,
                tuple(registro[campo] for campo in campos),
            )

        conexion.execute(
            """
            INSERT INTO migraciones (nombre)
            VALUES (?)
            """,
            (nombre,),
        )

    logger.info(
        "Migrados %s registros desde JSON.",
        len(historial),
    )

    return len(historial)
