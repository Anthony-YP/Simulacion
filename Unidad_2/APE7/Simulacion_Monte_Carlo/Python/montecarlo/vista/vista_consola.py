"""Presentación de resultados en la terminal."""
from __future__ import annotations

import math
from collections.abc import Sequence

from ..modelo.generador_lcg import ParametrosLCG
from ..modelo.resultados import FilaComparacion, ResultadoEstimacion, ResumenRepeticiones

ANCHO = 92


def _miles(n: int) -> str:
    """1000000 -> '1 000 000' (mismo formato que la tabla de la guía)."""
    return f"{n:,}".replace(",", " ")


class VistaConsola:
    def mostrar_encabezado(self, parametros: ParametrosLCG, lenguaje: str) -> None:
        print("=" * ANCHO)
        print(f"  ESTIMACIÓN DE π MEDIANTE EL MÉTODO DE MONTE CARLO  ({lenguaje})".center(ANCHO))
        print("=" * ANCHO)
        print("  Modelo:      π ≈ 4 · (Nc / N),  puntos en [-1, 1] x [-1, 1], círculo x² + y² <= 1")
        print("  Generador:   LCG  X(n+1) = (a · X(n) + c) mod m,  U(n) = X(n) / m")
        print(f"  Parámetros:  a = {parametros.a},  c = {parametros.c},  m = {parametros.m},  X0 = {parametros.semilla}")
        print(f"  Valor real:  π = {math.pi:.10f}")

    def mostrar_muestra_lcg(self, numeros: Sequence[float]) -> None:
        print("\n  Primeros números del LCG (verificación con la otra implementación):")
        for i, u in enumerate(numeros, start=1):
            print(f"    U({i:>2}) = {u:.10f}")

    def mostrar_resultados(self, resultados: Sequence[ResultadoEstimacion]) -> None:
        self._titulo("Tabla de resultados (una ejecución por tamaño de muestra)")
        print(f"  {'N':>11} {'Nc':>11} {'π estimado':>13} {'Error absoluto':>16} {'Error relativo':>16} {'Tiempo (ms)':>13}")
        for r in resultados:
            print(f"  {_miles(r.n_puntos):>11} {_miles(r.puntos_dentro):>11} {r.pi_estimado:>13.6f} "
                  f"{r.error_absoluto:>16.6f} {r.error_relativo:>15.4%} {r.tiempo_ms:>13.3f}")
        mejor = min(resultados, key=lambda r: r.error_absoluto)
        print(f"\n  Mejor aproximación: N = {_miles(mejor.n_puntos)}  (error = {mejor.error_absoluto:.6f})")

    def mostrar_repeticiones(self, resumenes: Sequence[ResumenRepeticiones]) -> None:
        if not resumenes:
            return
        self._titulo(f"Repeticiones con {resumenes[0].repeticiones} semillas distintas (variabilidad del error)")
        print(f"  {'N':>11} {'π promedio':>13} {'Desv. est.':>12} {'Error medio':>13} "
              f"{'Error mín.':>12} {'Error máx.':>12} {'1/√N':>10}")
        for r in resumenes:
            print(f"  {_miles(r.n_puntos):>11} {r.pi_promedio:>13.6f} {r.desviacion_pi:>12.6f} {r.error_promedio:>13.6f} "
                  f"{r.error_minimo:>12.6f} {r.error_maximo:>12.6f} {1 / math.sqrt(r.n_puntos):>10.6f}")

    def mostrar_comparacion(self, filas: Sequence[FilaComparacion]) -> None:
        self._titulo("Comparación Python vs Java")
        if not filas:
            print("  Aún no hay resultados de Java. Ejecute primero la versión Java y luego vuelva a ejecutar Python.")
            return
        print(f"  {'N':>11} {'π estimado':>13} {'Error':>11} {'T. Python (ms)':>15} {'T. Java (ms)':>14} "
              f"{'Py/Java':>9} {'¿Igual π?':>10}")
        for f in filas:
            pi = f"{f.pi_python:.6f}" if f.misma_estimacion else f"{f.pi_python:.4f}/{f.pi_java:.4f}"
            print(f"  {_miles(f.n_puntos):>11} {pi:>13} {f.error_python:>11.6f} {f.tiempo_python_ms:>15.3f} "
                  f"{f.tiempo_java_ms:>14.3f} {f.razon_tiempos:>8.1f}x {'sí' if f.misma_estimacion else 'no':>10}")

    def mostrar_archivos(self, rutas: Sequence[object]) -> None:
        self._titulo("Archivos generados")
        for ruta in rutas:
            print(f"  - {ruta}")
        print()

    @staticmethod
    def _titulo(texto: str) -> None:
        print("\n" + "-" * ANCHO)
        print(f"  {texto}")
        print("-" * ANCHO)
