import csv
import tempfile
import unittest
from pathlib import Path

from controller import SIRController
from model import SIRParameters, SIRSimulation


class TestSIRSimulation(unittest.TestCase):
    def test_101_registros_y_estado_inicial(self):
        results = SIRSimulation(SIRParameters()).run()

        self.assertEqual(len(results), 101)
        self.assertEqual([row.time for row in results], list(range(101)))

        first = results[0]
        self.assertEqual((first.susceptible, first.infected, first.recovered), (95, 5, 0))

    def test_poblacion_total_se_mantiene_en_100(self):
        results = SIRSimulation(SIRParameters()).run()

        for row in results:
            with self.subTest(time=row.time):
                total = row.susceptible + row.infected + row.recovered
                self.assertEqual(total, 100)

    def test_misma_semilla_produce_mismos_resultados(self):
        params = SIRParameters(seed=42)
        first_run = SIRSimulation(params).run()
        second_run = SIRSimulation(params).run()

        self.assertEqual(first_run, second_run)

    def test_beta_cero_evitar_contagios(self):
        params = SIRParameters(beta=0.0)
        results = SIRSimulation(params).run()

        self.assertTrue(all(row.susceptible == 95 for row in results))

    def test_controlador_exporta_csv_y_png(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            results = SIRController(SIRParameters(), output_dir=temp_dir).run()
            csv_path = Path(temp_dir) / "resultados_python.csv"
            png_path = Path(temp_dir) / "grafica_sir_python.png"

            self.assertTrue(csv_path.is_file())
            self.assertTrue(png_path.is_file())
            self.assertGreater(png_path.stat().st_size, 0)
            report_path = Path(temp_dir) / "reporte_python.html"
            self.assertIn(
                'src="grafica_sir_python.png"',
                report_path.read_text(encoding="utf-8"),
            )

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
