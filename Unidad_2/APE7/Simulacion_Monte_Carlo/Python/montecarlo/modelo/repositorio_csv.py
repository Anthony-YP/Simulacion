"""Lectura y escritura de resultados en CSV (formato compartido con la versión Java)."""
from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path

from .resultados import FilaComparacion, ResultadoEstimacion, ResumenRepeticiones

COLUMNAS_RESULTADOS = ["n_puntos", "puntos_dentro", "pi_estimado", "error_absoluto", "error_relativo", "tiempo_ms"]
COLUMNAS_REPETICIONES = [
    "n_puntos", "repeticiones", "pi_promedio", "desviacion_pi", "error_promedio", "error_minimo", "error_maximo",
]
COLUMNAS_COMPARACION = [
    "n_puntos", "pi_python", "pi_java", "error_python", "error_java",
    "tiempo_python_ms", "tiempo_java_ms", "misma_estimacion",
]


class RepositorioCSV:
    def __init__(self, carpeta: Path, lenguaje: str) -> None:
        self._carpeta = carpeta
        self._lenguaje = lenguaje

    @property
    def ruta_resultados(self) -> Path:
        return self._carpeta / f"resultados_{self._lenguaje}.csv"

    def guardar_resultados(self, resultados: Sequence[ResultadoEstimacion]) -> Path:
        filas = [
            [r.n_puntos, r.puntos_dentro, f"{r.pi_estimado:.10f}", f"{r.error_absoluto:.10f}",
             f"{r.error_relativo:.10f}", f"{r.tiempo_ms:.4f}"]
            for r in resultados
        ]
        return self._escribir(self.ruta_resultados, COLUMNAS_RESULTADOS, filas)

    def guardar_repeticiones(self, resumenes: Sequence[ResumenRepeticiones]) -> Path:
        filas = [
            [r.n_puntos, r.repeticiones, f"{r.pi_promedio:.10f}", f"{r.desviacion_pi:.10f}",
             f"{r.error_promedio:.10f}", f"{r.error_minimo:.10f}", f"{r.error_maximo:.10f}"]
            for r in resumenes
        ]
        return self._escribir(self._carpeta / f"repeticiones_{self._lenguaje}.csv", COLUMNAS_REPETICIONES, filas)

    def guardar_comparacion(self, filas_comparacion: Sequence[FilaComparacion]) -> Path:
        filas = [
            [f.n_puntos, f"{f.pi_python:.10f}", f"{f.pi_java:.10f}", f"{f.error_python:.10f}",
             f"{f.error_java:.10f}", f"{f.tiempo_python_ms:.4f}", f"{f.tiempo_java_ms:.4f}",
             "si" if f.misma_estimacion else "no"]
            for f in filas_comparacion
        ]
        return self._escribir(self._carpeta / "comparacion_python_java.csv", COLUMNAS_COMPARACION, filas)

    @staticmethod
    def leer_resultados(ruta: Path) -> list[ResultadoEstimacion]:
        """Lee un CSV de resultados (de cualquiera de los dos lenguajes). Devuelve [] si no existe."""
        if not ruta.exists():
            return []
        with ruta.open(encoding="utf-8", newline="") as archivo:
            return [
                ResultadoEstimacion(
                    n_puntos=int(fila["n_puntos"]),
                    puntos_dentro=int(fila["puntos_dentro"]),
                    pi_estimado=float(fila["pi_estimado"]),
                    error_absoluto=float(fila["error_absoluto"]),
                    error_relativo=float(fila["error_relativo"]),
                    tiempo_ms=float(fila["tiempo_ms"]),
                )
                for fila in csv.DictReader(archivo)
            ]

    def _escribir(self, ruta: Path, columnas: list[str], filas: list[list]) -> Path:
        self._carpeta.mkdir(parents=True, exist_ok=True)
        with ruta.open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(columnas)
            escritor.writerows(filas)
        return ruta
