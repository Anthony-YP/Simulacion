"""Pruebas de la Parte 3: exportación a CSV y gráfica.

También cubren el reporte HTML: su resumen (pico, fin del brote, tasa de
ataque) y la cuadrícula SVG de personas.
"""

import csv
import tempfile
import unittest
from pathlib import Path

from model import SIRParameters, SIRSimulation, StepResult
from view import ChartView, CsvExporter, ReportView

HEADER = "tiempo,susceptibles,infectados,recuperados"


class CsvExporterTest(unittest.TestCase):
    # setUp/tearDown crean y borran una carpeta temporal para cada prueba.
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_exports_full_simulation(self) -> None:
        """El CSV tiene encabezado, 101 filas, inicio 0,95,5,0 y cada fila suma 100."""
        results = SIRSimulation(SIRParameters()).run()
        # La subcarpeta no existe: también se verifica que el exportador la crea.
        path = self.tmp / "salida" / "resultados.csv"

        CsvExporter.export(results, path)

        lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], HEADER)
        self.assertEqual(len(lines) - 1, 101)
        self.assertEqual(lines[1], "0,95,5,0")
        with path.open(newline="", encoding="utf-8") as file:
            rows = list(csv.reader(file))[1:]
        for row in rows:
            self.assertEqual(sum(int(value) for value in row[1:]), 100)

    def test_exact_content_for_small_list(self) -> None:
        """Con datos pequeños el archivo coincide byte a byte con lo esperado."""
        results = [StepResult(0, 9, 1, 0), StepResult(1, 8, 1, 1)]
        path = self.tmp / "pequeno.csv"

        CsvExporter.export(results, str(path))

        # El módulo csv termina cada fila con \r\n por defecto.
        content = path.read_bytes().decode("utf-8")
        self.assertEqual(content, f"{HEADER}\r\n0,9,1,0\r\n1,8,1,1\r\n")


class ChartViewTest(unittest.TestCase):
    def test_creates_non_empty_image(self) -> None:
        """La gráfica se guarda como archivo PNG no vacío."""
        results = SIRSimulation(SIRParameters()).run()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "graficas" / "sir.png"

            ChartView.plot(results, path)

            self.assertTrue(path.is_file())
            self.assertGreater(path.stat().st_size, 0)


class ReportViewTest(unittest.TestCase):
    def test_report_explains_practice_and_shows_results(self) -> None:
        """El HTML incluye título, R0 = 3.00, la imagen y una fila por instante."""
        params = SIRParameters()
        results = SIRSimulation(params).run()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reporte" / "reporte_python.html"

            ReportView.render(results, params, path, chart_file="grafica.png")

            html = path.read_text(encoding="utf-8")
        self.assertIn("Modelo SIR", html)
        # R0 = beta / gamma = 0.30 / 0.10 = 3.
        self.assertIn("R₀ = β / γ = 3.00", html)
        self.assertIn('src="grafica.png"', html)
        self.assertIn("<td>0</td><td>95</td><td>5</td><td>0</td>", html)
        self.assertEqual(html.count("<tr class=\"row\">"), 101)

    def test_summary_reports_peak_of_infected(self) -> None:
        """El resumen calcula pico, estado final y tasa de ataque con datos conocidos."""
        results = [
            StepResult(0, 9, 1, 0),
            StepResult(1, 6, 4, 0),
            StepResult(2, 5, 3, 2),
        ]

        summary = ReportView.summary(results)

        self.assertEqual(summary["peak_infected"], 4)
        self.assertEqual(summary["peak_time"], 1)
        self.assertEqual(summary["final"], results[-1])
        # Población 10 y quedan 5 susceptibles: se infectaron 5, es decir, el 50 %.
        self.assertEqual(summary["attack_rate"], 50.0)
        # Nunca llega a 0 infectados, así que no hay fin del brote.
        self.assertIsNone(summary["end_time"])

    def test_population_grid_draws_one_person_per_individual(self) -> None:
        """La cuadrícula SVG dibuja un muñequito por persona con la clase de su estado."""
        grid = ReportView.population_grid(StepResult(0, 95, 5, 0))

        self.assertEqual(grid.count('class="ps"'), 95)
        self.assertEqual(grid.count('class="pi"'), 5)
        self.assertEqual(grid.count('class="pr"'), 0)

    def test_report_shows_population_at_start_peak_and_end(self) -> None:
        """El reporte incluye tres cuadrículas (inicio, pico y final) de 100 personas."""
        params = SIRParameters()
        results = SIRSimulation(params).run()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reporte_python.html"
            ReportView.render(results, params, path)
            html = path.read_text(encoding="utf-8")

        # 3 cuadrículas x 100 personas = 300 referencias al símbolo "person".
        self.assertEqual(html.count('href="#person"'), 300)
        self.assertIn("Al inicio · t = 0", html)
        self.assertIn("Al final · t = 100", html)

    def test_summary_reports_when_outbreak_ends(self) -> None:
        """El fin del brote es el primer instante con 0 infectados."""
        results = [StepResult(0, 9, 1, 0), StepResult(1, 9, 0, 1), StepResult(2, 9, 0, 1)]

        self.assertEqual(ReportView.summary(results)["end_time"], 1)


if __name__ == "__main__":
    unittest.main()
