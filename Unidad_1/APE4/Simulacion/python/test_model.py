"""Pruebas del modelo SIR (Partes 1 y 2) y del controlador.

Comprueban el número de registros, la conservación de la población, la
reproducibilidad con semilla, el caso beta = 0 y los archivos exportados.
"""

import csv
import tempfile
import unittest
from pathlib import Path

from controller import SIRController
from model import SIRParameters, SIRSimulation


class TestSIRSimulation(unittest.TestCase):
    def test_101_registros_y_estado_inicial(self):
        """De t = 0 a t = 100 hay 101 registros y el inicio es 95 S, 5 I, 0 R."""
        results = SIRSimulation(SIRParameters()).run()

        self.assertEqual(len(results), 101)
        self.assertEqual([row.time for row in results], list(range(101)))

        first = results[0]
        self.assertEqual((first.susceptible, first.infected, first.recovered), (95, 5, 0))

    def test_poblacion_total_se_mantiene_en_100(self):
        """En todo instante se cumple N = S + I + R = 100."""
        results = SIRSimulation(SIRParameters()).run()

        for row in results:
            # subTest indica en qué instante falla, si alguno falla.
            with self.subTest(time=row.time):
                total = row.susceptible + row.infected + row.recovered
                self.assertEqual(total, 100)

    def test_misma_semilla_produce_mismos_resultados(self):
        """Dos ejecuciones con la misma semilla dan exactamente los mismos resultados."""
        params = SIRParameters(seed=42)
        first_run = SIRSimulation(params).run()
        second_run = SIRSimulation(params).run()

        # Las dataclasses se comparan campo a campo, así que se compara cada fila completa.
        self.assertEqual(first_run, second_run)

    def test_beta_cero_evitar_contagios(self):
        """Con beta = 0 nadie se contagia: los susceptibles se mantienen en 95."""
        params = SIRParameters(beta=0.0)
        results = SIRSimulation(params).run()

        self.assertTrue(all(row.susceptible == 95 for row in results))

    def test_controlador_exporta_csv_y_png(self):
        """El controlador genera CSV, PNG y HTML con el contenido esperado."""
        # Carpeta temporal: se borra al terminar y no ensucia el proyecto.
        with tempfile.TemporaryDirectory() as temp_dir:
            results = SIRController(SIRParameters(), output_dir=temp_dir).run()
            csv_path = Path(temp_dir) / "resultados_python.csv"
            png_path = Path(temp_dir) / "grafica_sir_python.png"

            self.assertTrue(csv_path.is_file())
            self.assertTrue(png_path.is_file())
            self.assertGreater(png_path.stat().st_size, 0)
            # El reporte debe enlazar la gráfica con una ruta relativa.
            report_path = Path(temp_dir) / "reporte_python.html"
            self.assertIn(
                'src="grafica_sir_python.png"',
                report_path.read_text(encoding="utf-8"),
            )

            # Se verifica el encabezado de la guía y la primera fila del CSV.
            with csv_path.open("r", newline="", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                self.assertEqual(
                    reader.fieldnames,
                    ["tiempo", "susceptibles", "infectados", "recuperados"],
                )
                rows = list(reader)

            self.assertEqual(len(rows), 101)
            self.assertEqual(
                rows[0],
                {
                    "tiempo": "0",
                    "susceptibles": "95",
                    "infectados": "5",
                    "recuperados": "0",
                },
            )
            self.assertEqual(len(results), len(rows))


if __name__ == "__main__":
    unittest.main()
