
import json
import tempfile
import unittest
from pathlib import Path

from taximeter import Carrera, guardar_carrera, cargar_tarifas
from taximeter import TARIFA_PARADO, TARIFA_MOVIMIENTO
from taximetro.taximetro import Taximetro


class TestCarrera(unittest.TestCase):

    def test_tarifa_parado_10_segundos(self):
        carrera = Carrera(inicio=0)
        self.assertAlmostEqual(carrera.finalizar(10), 0.20)

    def test_tarifa_movimiento_10_segundos(self):
        carrera = Carrera(inicio=0)
        carrera.cambiar_estado("movimiento", 0)
        self.assertAlmostEqual(carrera.finalizar(10), 0.50)

    def test_cambio_de_estado(self):
        carrera = Carrera(inicio=0)
        carrera.cambiar_estado("movimiento", 10)
        self.assertAlmostEqual(carrera.finalizar(20), 0.70)

    def test_varios_cambios_de_estado(self):
        carrera = Carrera(inicio=0)
        carrera.cambiar_estado("movimiento", 5)
        carrera.cambiar_estado("parado", 15)
        self.assertAlmostEqual(carrera.finalizar(20), 0.70)

    def test_estado_invalido(self):
        carrera = Carrera(inicio=0)

        with self.assertRaises(ValueError):
            carrera.cambiar_estado("volando", 5)

    def test_dos_carreras_independientes(self):
        primera = Carrera(inicio=0)
        importe_primera = primera.finalizar(10)

        segunda = Carrera(inicio=20)
        importe_segunda = segunda.finalizar(30)

        self.assertAlmostEqual(importe_primera, 0.20)
        self.assertAlmostEqual(importe_segunda, 0.20)

    def test_guarda_una_carrera(self):
        with tempfile.TemporaryDirectory() as temporal:
            archivo = Path(temporal) / "data" / "historial.json"

            carrera = Carrera(inicio=0)
            carrera.finalizar(10)

            guardar_carrera(carrera, archivo)

            with archivo.open("r", encoding="utf-8") as fichero:
                historial = json.load(fichero)

            self.assertEqual(len(historial), 1)
            self.assertEqual(historial[0]["duracion_segundos"], 10)
            self.assertEqual(historial[0]["importe_euros"], 0.20)
            self.assertIn("fecha_inicio", historial[0])

    def test_conserva_varias_carreras(self):
        with tempfile.TemporaryDirectory() as temporal:
            archivo = Path(temporal) / "data" / "historial.json"

            primera = Carrera(inicio=0)
            primera.finalizar(10)

            segunda = Carrera(inicio=20)
            segunda.finalizar(30)

            guardar_carrera(primera, archivo)
            guardar_carrera(segunda, archivo)

            with archivo.open("r", encoding="utf-8") as fichero:
                historial = json.load(fichero)

            self.assertEqual(len(historial), 2)

    def test_historial_es_json_valido(self):
        with tempfile.TemporaryDirectory() as temporal:
            archivo = Path(temporal) / "historial.json"

            carrera = Carrera(inicio=0)
            carrera.finalizar(5)
            guardar_carrera(carrera, archivo)

            contenido = archivo.read_text(encoding="utf-8")
            historial = json.loads(contenido)

            self.assertIsInstance(historial, list)
            self.assertIsInstance(historial[0], dict)

    def test_carga_tarifas_desde_json(self):
        with tempfile.TemporaryDirectory() as temporal:
            archivo = Path(temporal) / "config.json"

            configuracion = {
                "tarifa_parado": 0.10,
                "tarifa_movimiento": 0.50,
            }

            archivo.write_text(
                json.dumps(configuracion),
                encoding="utf-8",
            )

            tarifas = cargar_tarifas(archivo)

            self.assertEqual(tarifas, (0.10, 0.50))

    def test_tarifas_predeterminadas_si_falta_archivo(self):
        with tempfile.TemporaryDirectory() as temporal:
            archivo = Path(temporal) / "inexistente.json"

            tarifas = cargar_tarifas(archivo)

            self.assertEqual(
                tarifas,
                (TARIFA_PARADO, TARIFA_MOVIMIENTO),
            )

    def test_tarifas_predeterminadas_si_valores_invalidos(self):
        with tempfile.TemporaryDirectory() as temporal:
            archivo = Path(temporal) / "config.json"

            configuracion = {
                "tarifa_parado": -0.10,
                "tarifa_movimiento": 0.50,
            }

            archivo.write_text(
                json.dumps(configuracion),
                encoding="utf-8",
            )

            tarifas = cargar_tarifas(archivo)

            self.assertEqual(
                tarifas,
                (TARIFA_PARADO, TARIFA_MOVIMIENTO),
            )


class TestTaximetro(unittest.TestCase):

    def test_iniciar_carrera(self):
        taximetro = Taximetro()

        carrera = taximetro.iniciar_carrera()

        self.assertIsNotNone(carrera)
        self.assertTrue(taximetro.hay_carrera_activa())

    def test_no_permite_dos_carreras_activas(self):
        taximetro = Taximetro()
        taximetro.iniciar_carrera()

        with self.assertRaises(RuntimeError):
            taximetro.iniciar_carrera()

    def test_cambiar_estado_sin_carrera_activa(self):
        taximetro = Taximetro()

        with self.assertRaises(RuntimeError):
            taximetro.cambiar_estado("movimiento")

    def test_finalizar_sin_carrera_activa(self):
        taximetro = Taximetro()

        with self.assertRaises(RuntimeError):
            taximetro.finalizar_carrera()

    def test_finalizar_carrera_libera_el_taximetro(self):
        taximetro = Taximetro()
        taximetro.iniciar_carrera()

        carrera = taximetro.finalizar_carrera()

        self.assertIsNotNone(carrera)
        self.assertFalse(taximetro.hay_carrera_activa())

    def test_permite_iniciar_otra_carrera(self):
        taximetro = Taximetro()
        taximetro.iniciar_carrera()
        taximetro.finalizar_carrera()

        segunda_carrera = taximetro.iniciar_carrera()

        self.assertIsNotNone(segunda_carrera)
        self.assertTrue(taximetro.hay_carrera_activa())


if __name__ == "__main__":
    unittest.main(verbosity=2)
