"""Controlador del patrón MVC: coordina el modelo SIR y las vistas de salida.

El controlador no calcula la epidemia ni dibuja nada: solo ejecuta el modelo
y entrega sus resultados a cada vista (CSV, gráfica y reporte HTML).
"""

from pathlib import Path

from model import SIRParameters, SIRSimulation
from view import CsvExporter, ChartView, ReportView


class SIRController:
    """Conecta el modelo de simulación con sus vistas de salida."""

    def __init__(self, params: SIRParameters, output_dir: str | Path = ".") -> None:
        self.params = params
        # output_dir es configurable para que las pruebas escriban en una carpeta temporal.
        self.output_dir = Path(output_dir)
        # Se guarda como atributo para que main.py pueda abrir el reporte en el navegador.
        self.report_path = self.output_dir / "reporte_python.html"

    def run(self):
        """Ejecuta el modelo, guarda el CSV, crea la gráfica y el reporte HTML."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Modelo: ejecuta la simulación y obtiene la lista de StepResult.
        simulation = SIRSimulation(self.params)
        results = simulation.run()

        csv_path = self.output_dir / "resultados_python.csv"
        chart_path = self.output_dir / "grafica_sir_python.png"

        # 2. Vistas: cada una presenta los mismos resultados en un formato distinto.
        CsvExporter().export(results, str(csv_path))
        ChartView().plot(results, str(chart_path))
        # Se pasa solo el nombre de la imagen para que el HTML la enlace con una ruta relativa.
        ReportView().render(
            results, self.params, self.report_path, chart_file=chart_path.name
        )

        return results
