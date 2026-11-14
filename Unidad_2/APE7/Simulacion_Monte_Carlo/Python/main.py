"""Estimación de π mediante el método de Monte Carlo (versión Python).

Uso:
    python3 main.py                          # Práctica completa (N = 1 000 ... 1 000 000)
    python3 main.py --tamanios 1000 10000    # Solo algunos tamaños
    python3 main.py --semilla 2026           # Otra semilla del LCG
    python3 main.py --repeticiones 30        # Más semillas para analizar el error
    python3 main.py --sin-graficos           # Solo tablas y CSV
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from montecarlo.controlador.controlador_simulacion import ConfiguracionSimulacion, ControladorSimulacion
from montecarlo.modelo.repositorio_csv import RepositorioCSV
from montecarlo.vista.vista_consola import VistaConsola
from montecarlo.vista.vista_graficos import VistaGraficos

DIRECTORIO = Path(__file__).resolve().parent
CARPETA_RESULTADOS = DIRECTORIO / "Resultados"
RESULTADOS_JAVA = DIRECTORIO.parent / "Java" / "Resultados" / "resultados_java.csv"


def leer_argumentos() -> argparse.Namespace:
    lector = argparse.ArgumentParser(description="Estimación de π con Monte Carlo y un generador LCG.")
    lector.add_argument("--tamanios", type=int, nargs="+", help="Valores de N (puntos) a evaluar.")
    lector.add_argument("--semilla", type=int, help="Semilla X0 del LCG (por defecto 12345).")
    lector.add_argument("--repeticiones", type=int, help="Semillas distintas por cada N (por defecto 10; 1 = ninguna).")
    lector.add_argument("--sin-graficos", action="store_true", help="No genera las imágenes PNG.")
    return lector.parse_args()


def crear_configuracion(args: argparse.Namespace) -> ConfiguracionSimulacion:
    config = ConfiguracionSimulacion()
    cambios: dict[str, object] = {}
    if args.tamanios:
        if any(n <= 0 for n in args.tamanios):
            raise SystemExit("Error: cada N debe ser mayor que 0.")
        cambios["tamanios"] = tuple(args.tamanios)
    if args.semilla is not None:
        try:
            cambios["parametros"] = config.parametros.con_semilla(args.semilla)
        except ValueError as error:
            raise SystemExit(f"Error: {error}") from error
    if args.repeticiones is not None:
        if args.repeticiones < 1:
            raise SystemExit("Error: las repeticiones deben ser al menos 1.")
        cambios["repeticiones"] = args.repeticiones
    if args.sin_graficos:
        cambios["generar_graficos"] = False
    return replace(config, **cambios)


def main() -> None:
    controlador = ControladorSimulacion(
        configuracion=crear_configuracion(leer_argumentos()),
        repositorio=RepositorioCSV(CARPETA_RESULTADOS, "python"),
        vista=VistaConsola(),
        graficos=VistaGraficos(CARPETA_RESULTADOS),
        resultados_java=RESULTADOS_JAVA,
    )
    controlador.ejecutar()


if __name__ == "__main__":
    main()
