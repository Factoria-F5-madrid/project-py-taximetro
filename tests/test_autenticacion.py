
import json
import tempfile
import unittest
from pathlib import Path

from taximetro.autenticacion import (
    crear_credenciales,
    verificar_contrasena,
    credenciales_configuradas,
    ErrorAutenticacion,
)


class TestAutenticacion(unittest.TestCase):

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.archivo = Path(self.temporal.name) / "data" / "credenciales.json"

    def tearDown(self):
        self.temporal.cleanup()

    def test_crear_credenciales(self):
        crear_credenciales("TaxiTech2026", self.archivo)

        self.assertTrue(credenciales_configuradas(self.archivo))

    def test_contrasena_correcta(self):
        crear_credenciales("TaxiTech2026", self.archivo)

        self.assertTrue(
            verificar_contrasena("TaxiTech2026", self.archivo)
        )

    def test_contrasena_incorrecta(self):
        crear_credenciales("TaxiTech2026", self.archivo)

        self.assertFalse(
            verificar_contrasena("OtraClave2026", self.archivo)
        )

    def test_no_guarda_contrasena_original(self):
        contrasena = "TaxiTech2026"
        crear_credenciales(contrasena, self.archivo)

        contenido = self.archivo.read_text(encoding="utf-8")

        self.assertNotIn(contrasena, contenido)

    def test_salt_diferente_en_cada_creacion(self):
        otro_archivo = Path(self.temporal.name) / "segunda.json"

        crear_credenciales("TaxiTech2026", self.archivo)
        crear_credenciales("TaxiTech2026", otro_archivo)

        datos_1 = json.loads(self.archivo.read_text(encoding="utf-8"))
        datos_2 = json.loads(otro_archivo.read_text(encoding="utf-8"))

        self.assertNotEqual(datos_1["sal"], datos_2["sal"])

    def test_rechaza_contrasena_corta(self):
        with self.assertRaises(ValueError):
            crear_credenciales("123", self.archivo)

    def test_archivo_inexistente(self):
        with self.assertRaises(ErrorAutenticacion):
            verificar_contrasena("TaxiTech2026", self.archivo)

    def test_archivo_danado(self):
        self.archivo.parent.mkdir(parents=True, exist_ok=True)
        self.archivo.write_text("{ JSON incorrecto", encoding="utf-8")

        with self.assertRaises(ErrorAutenticacion):
            verificar_contrasena("TaxiTech2026", self.archivo)


if __name__ == "__main__":
    unittest.main()
