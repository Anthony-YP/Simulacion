"""Punto de entrada de la versión Python del Generador Congruencial Lineal.

Es la "raíz de composición": aquí, y solo aquí, se crean las clases concretas
del modelo y de las vistas, que luego se inyectan al controlador.

Uso:
    python main.py                      # procedimiento completo con los valores de la práctica
    python main.py --semilla 2024       # otra semilla principal
    python main.py --help               # todas las opciones
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lcg.controlador import (
    A_PRACTICA,
    C_PRACTICA,
    CANTIDAD_PRACTICA,
    FILAS_TABLA,
    M_PRACTICA,
    SEMILLA_ALTERNATIVA,
    SEMILLA_PRACTICA,
    ConfiguracionSimulacion,
    ControladorSimulacion,
)
from lcg.modelo import (
    AnalizadorEstadistico,
    AnalizadorPeriodo,
    ComparadorSecuencias,
    GeneradorCongruencialLineal,
    ParametrosLCG,
    RepositorioCSV,
)
from lcg.vista import VistaConsola, VistaGraficos

# Las rutas por defecto se calculan desde este archivo para que el programa
# funcione igual sin importar desde qué carpeta se ejecute.
CARPETA_PYTHON = Path(__file__).resolve().parent
CARPETA_JAVA = CARPETA_PYTHON.parent / "Java"


def crear_analizador_argumentos() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generador Congruencial Lineal: X(n+1) = (a*X(n) + c) mod m,  U(n) = X(n)/m.",
    )
    parser.add_argument("--a", type=int, default=A_PRACTICA, help="multiplicador (defecto: %(default)s)")
    parser.add_argument("--c", type=int, default=C_PRACTICA, help="incremento (defecto: %(default)s)")
    parser.add_argument("--m", type=int, default=M_PRACTICA, help="módulo (defecto: 2^32 = %(default)s)")
    parser.add_argument("--semilla", type=int, default=SEMILLA_PRACTICA,
                        help="semilla X(0) (defecto: %(default)s)")
    parser.add_argument("--semilla-alternativa", type=int, default=SEMILLA_ALTERNATIVA,
                        help="semilla del paso 7 (defecto: %(default)s)")
    parser.add_argument("--n", type=int, default=CANTIDAD_PRACTICA, dest="cantidad",
                        help="valores a generar (defecto: %(default)s)")
    parser.add_argument("--filas", type=int, default=FILAS_TABLA,
                        help="filas de las tablas de consola (defecto: %(default)s)")
    parser.add_argument("--periodo-completo", action="store_true",
                        help="mide el ciclo completo con el algoritmo de Brent "
                             "(con m = 2^32: unos 33 min en Python y 70 s en Java)")
    parser.add_argument("--resultados", type=Path, default=CARPETA_PYTHON / "resultados",
                        help="carpeta de salida (defecto: Python/resultados)")
    parser.add_argument("--comparar-con", type=Path, default=CARPETA_JAVA / "resultados",
                        help="carpeta con los CSV de la versión Java (defecto: Java/resultados)")
    parser.add_argument("--sin-graficas", action="store_true",
                        help="omite las gráficas (no necesita matplotlib)")
    return parser


def crear_vista_graficos(parser: argparse.ArgumentParser) -> VistaGraficos:
    """Importa matplotlib solo cuando se necesitan gráficas."""
    try:
        from lcg.vista.vista_graficos import VistaGraficosMatplotlib
    except ImportError:
        parser.error("matplotlib no está instalado: ejecute 'pip install -r requirements.txt' o use --sin-graficas.")
    return VistaGraficosMatplotlib()


def main(argumentos: list[str] | None = None) -> int:
    parser = crear_analizador_argumentos()
    args = parser.parse_args(argumentos)
    try:
        configuracion = ConfiguracionSimulacion(
            parametros=ParametrosLCG(a=args.a, c=args.c, m=args.m, semilla=args.semilla),
            semilla_alternativa=args.semilla_alternativa,
            cantidad=args.cantidad,
            filas_tabla=args.filas,
            periodo_completo=args.periodo_completo,
            directorio_resultados=args.resultados,
            directorio_externo=args.comparar_con,
        )
    except ValueError as error:
        parser.error(str(error))

    controlador = ControladorSimulacion(
        configuracion=configuracion,
        fabrica_generador=GeneradorCongruencialLineal,
        analizador_periodo=AnalizadorPeriodo(),
        analizador_estadistico=AnalizadorEstadistico(),
        comparador=ComparadorSecuencias(),
        repositorio=RepositorioCSV(),
        vista=VistaConsola(),
        graficos=None if args.sin_graficas else crear_vista_graficos(parser),
    )
    controlador.ejecutar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
