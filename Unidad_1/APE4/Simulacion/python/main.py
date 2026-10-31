"""Punto de entrada del programa: ejecuta la simulación SIR y muestra un resumen.

Uso: `python main.py` (añadir `--sin-navegador` para no abrir el reporte HTML).
"""

import sys
import webbrowser

from controller import SIRController
from model import SIRParameters


def main() -> None:
    """Crea los parámetros, ejecuta el controlador e imprime el estado final."""
    params = SIRParameters()  # 100, 5, 0.30, 0.10, 100, semilla 42
    controller = SIRController(params)
    results = controller.run()

    # El último registro corresponde a t = max_time.
    last = results[-1]
    print("Simulación SIR finalizada correctamente.")
    print(
        "Archivos creados: resultados_python.csv, grafica_sir_python.png "
        "y reporte_python.html"
    )
    print(
        f"Tiempo final: {last.time} | "
        f"Susceptibles: {last.susceptible} | "
        f"Infectados: {last.infected} | "
        f"Recuperados: {last.recovered}"
    )

    # Abre el reporte en el navegador, salvo con --sin-navegador
    if "--sin-navegador" not in sys.argv:
        # as_uri() necesita una ruta absoluta, por eso se usa resolve() antes.
        webbrowser.open(controller.report_path.resolve().as_uri())


# Solo se ejecuta al lanzar el archivo directamente, no al importarlo.
if __name__ == "__main__":
    main()
