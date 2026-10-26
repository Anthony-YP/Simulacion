from pathlib import Path

from controller.simulacion_controller import SimulacionController


def main() -> None:
    carpeta = Path(__file__).parent / "resultados"
    SimulacionController(carpeta).ejecutar()


if __name__ == "__main__":
    main()
