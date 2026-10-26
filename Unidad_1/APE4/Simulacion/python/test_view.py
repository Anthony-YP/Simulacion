"""Pruebas de la Parte 3: exportación a CSV y gráfica."""

import csv
import tempfile
import unittest
from pathlib import Path

from model import SIRParameters, SIRSimulation, StepResult
from view import ChartView, CsvExporter, ReportView

HEADER = "tiempo,susceptibles,infectados,recuperados"


class CsvExporterTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_exports_full_simulation(self) -> None:
        results = SIRSimulation(SIRParameters()).run()
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
        results = [StepResult(0, 9, 1, 0), StepResult(1, 8, 1, 1)]
        path = self.tmp / "pequeno.csv"

        CsvExporter.export(results, str(path))

        content = path.read_bytes().decode("utf-8")
        self.assertEqual(content, f"{HEADER}\r\n0,9,1,0\r\n1,8,1,1\r\n")


class ChartViewTest(unittest.TestCase):
    def test_creates_non_empty_image(self) -> None:
        results = SIRSimulation(SIRParameters()).run()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "graficas" / "sir.png"

            ChartView.plot(results, path)

            self.assertTrue(path.is_file())
            self.assertGreater(path.stat().st_size, 0)


class ReportViewTest(unittest.TestCase):
    def test_report_explains_practice_and_shows_results(self) -> None:
        params = SIRParameters()
        results = SIRSimulation(params).run()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reporte" / "reporte_python.html"

            ReportView.render(results, params, path, chart_file="grafica.png")

            html = path.read_text(encoding="utf-8")
        self.assertIn("Modelo SIR", html)
        self.assertIn("R₀ = β / γ = 3.00", html)
        self.assertIn('src="grafica.png"', html)
        self.assertIn("<td>0</td><td>95</td><td>5</td><td>0</td>", html)
        self.assertEqual(html.count("<tr class=\"row\">"), 101)

    def test_summary_reports_peak_of_infected(self) -> None:
        results = [
            StepResult(0, 9, 1, 0),
            StepResult(1, 6, 4, 0),
            StepResult(2, 5, 3, 2),
        ]

        summary = ReportView.summary(results)

        self.assertEqual(summary["peak_infected"], 4)
        self.assertEqual(summary["peak_time"], 1)
        self.assertEqual(summary["final"], results[-1])
        self.assertEqual(summary["attack_rate"], 50.0)
        self.assertIsNone(summary["end_time"])

    def test_population_grid_draws_one_person_per_individual(self) -> None:
        grid = ReportView.population_grid(StepResult(0, 95, 5, 0))

        self.assertEqual(grid.count('class="ps"'), 95)
        self.assertEqual(grid.count('class="pi"'), 5)
        self.assertEqual(grid.count('class="pr"'), 0)

    def test_report_shows_population_at_start_peak_and_end(self) -> None:
        params = SIRParameters()
        results = SIRSimulation(params).run()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reporte_python.html"
            ReportView.render(results, params, path)
            html = path.read_text(encoding="utf-8")

        self.assertEqual(html.count('href="#person"'), 300)
        self.assertIn("Al inicio · t = 0", html)
        self.assertIn("Al final · t = 100", html)

    def test_summary_reports_when_outbreak_ends(self) -> None:
        results = [StepResult(0, 9, 1, 0), StepResult(1, 9, 0, 1), StepResult(2, 9, 0, 1)]

        self.assertEqual(ReportView.summary(results)["end_time"], 1)


if __name__ == "__main__":
    unittest.main()
