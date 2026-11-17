
"""Autenticación segura para TAXITECH NEO//DRIVE."""

import hashlib
import hmac
import json
import secrets
from pathlib import Path


ITERACIONES = 600_000
LONGITUD_SAL = 16
LONGITUD_HASH = 32

DIRECTORIO_PROYECTO = Path(__file__).resolve().parent.parent
ARCHIVO_CREDENCIALES = (
    DIRECTORIO_PROYECTO / "data" / "credenciales.json"
)


class ErrorAutenticacion(Exception):
    """Error relacionado con la autenticación."""


def _derivar_hash(contrasena: str, sal: bytes, iteraciones: int) -> bytes:
    """Deriva un hash seguro a partir de la contraseña y la sal."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        sal,
        iteraciones,
        dklen=LONGITUD_HASH,
    )


def credenciales_configuradas(
    archivo: Path = ARCHIVO_CREDENCIALES,
) -> bool:
    """Indica si existe el archivo de credenciales."""
    return archivo.is_file()


def crear_credenciales(
    contrasena: str,
    archivo: Path = ARCHIVO_CREDENCIALES,
) -> None:
    """Crea y guarda las credenciales sin almacenar la contraseña original."""

    if not isinstance(contrasena, str) or len(contrasena) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")

    sal = secrets.token_bytes(LONGITUD_SAL)
    hash_contrasena = _derivar_hash(contrasena, sal, ITERACIONES)

    datos = {
        "algoritmo": "PBKDF2-HMAC-SHA256",
        "iteraciones": ITERACIONES,
        "sal": sal.hex(),
        "hash": hash_contrasena.hex(),
    }

    archivo.parent.mkdir(parents=True, exist_ok=True)

    temporal = archivo.with_suffix(".tmp")
    temporal.write_text(
        json.dumps(datos, indent=4),
        encoding="utf-8",
    )
    temporal.replace(archivo)


def verificar_contrasena(
    contrasena: str,
    archivo: Path = ARCHIVO_CREDENCIALES,
) -> bool:
    """Comprueba una contraseña contra las credenciales almacenadas."""

    if not archivo.is_file():
        raise ErrorAutenticacion(
            "No existe un archivo de credenciales configurado."
        )

    try:
        datos = json.loads(archivo.read_text(encoding="utf-8"))

        if datos["algoritmo"] != "PBKDF2-HMAC-SHA256":
            raise ValueError("Algoritmo no reconocido.")

        iteraciones = datos["iteraciones"]
        sal = bytes.fromhex(datos["sal"])
        hash_guardado = bytes.fromhex(datos["hash"])

        if (
            not isinstance(iteraciones, int)
            or iteraciones < 1
            or len(sal) != LONGITUD_SAL
            or len(hash_guardado) != LONGITUD_HASH
        ):
            raise ValueError("Credenciales no válidas.")

        hash_calculado = _derivar_hash(
            contrasena,
            sal,
            iteraciones,
        )

        return hmac.compare_digest(hash_guardado, hash_calculado)

    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ErrorAutenticacion(
            "El archivo de credenciales está dañado o no es válido."
        ) from error

def autenticar_consola() -> bool:
    """Solicita la contraseña desde la consola."""
    from getpass import getpass

    if not credenciales_configuradas():
        print("\nPrimera ejecución: configura tu contraseña.")
        while True:
            primera = getpass("Nueva contraseña: ")
            segunda = getpass("Confirma la contraseña: ")

            if primera != segunda:
                print("Las contraseñas no coinciden.")
                continue

            try:
                crear_credenciales(primera)
                print("Contraseña configurada correctamente.")
                return True
            except ValueError as error:
                print(error)

    for intento in range(3):
        contrasena = getpass("Contraseña de TAXITECH: ")

        try:
            if verificar_contrasena(contrasena):
                return True
        except ErrorAutenticacion as error:
            print(f"Error de autenticación: {error}")
            return False

        print("Contraseña incorrecta.")

    print("Acceso denegado.")
    return False

def autenticar_grafica() -> bool:
    """Solicita la contraseña mediante una ventana gráfica."""
    import tkinter as tk
    from tkinter import simpledialog, messagebox

    root = tk.Tk()
    root.withdraw()

    try:
        if not credenciales_configuradas():
            messagebox.showinfo(
                "Configuración inicial",
                "Configura tu contraseña para TAXITECH.",
                parent=root,
            )

            while True:
                primera = simpledialog.askstring(
                    "Nueva contraseña",
                    "Introduce una contraseña de al menos 8 caracteres:",
                    show="*",
                    parent=root,
                )

                if primera is None:
                    return False

                segunda = simpledialog.askstring(
                    "Confirmar contraseña",
                    "Repite la contraseña:",
                    show="*",
                    parent=root,
                )

                if segunda is None:
                    return False

                if primera != segunda:
                    messagebox.showerror(
                        "Error",
                        "Las contraseñas no coinciden.",
                        parent=root,
                    )
                    continue

                try:
                    crear_credenciales(primera)
                    return True
                except (ValueError, OSError, ErrorAutenticacion) as error:
                    messagebox.showerror("Error", str(error), parent=root)
                    return False

        for _ in range(3):
            contrasena = simpledialog.askstring(
                "Acceso a TAXITECH",
                "Introduce tu contraseña:",
                show="*",
                parent=root,
            )

            if contrasena is None:
                return False

            try:
                if verificar_contrasena(contrasena):
                    return True
            except ErrorAutenticacion as error:
                messagebox.showerror(
                    "Error de autenticación",
                    str(error),
                    parent=root,
                )
                return False

            messagebox.showerror(
                "Acceso denegado",
                "Contraseña incorrecta.",
                parent=root,
            )

        return False

    finally:
        root.destroy()
