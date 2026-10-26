import sys
import webbrowser

from controller import SIRController
from model import SIRParameters


def main() -> None:
    params = SIRParameters()  # 100, 5, 0.30, 0.10, 100, semilla 42
    controller = SIRController(params)
    results = controller.run()

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
        webbrowser.open(controller.report_path.resolve().as_uri())


if __name__ == "__main__":
    main()
