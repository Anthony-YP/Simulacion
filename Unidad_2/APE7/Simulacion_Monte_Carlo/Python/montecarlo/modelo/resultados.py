"""Estructuras inmutables con los datos que produce la simulación."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ResultadoEstimacion:
    """Una ejecución del experimento con N puntos (una fila de la tabla de la guía)."""

    n_puntos: int
    puntos_dentro: int
    pi_estimado: float
    error_absoluto: float
    error_relativo: float
    tiempo_ms: float


@dataclass(frozen=True)
class ResumenRepeticiones:
    """Estadísticos de R ejecuciones independientes (semillas distintas) con el mismo N."""

    n_puntos: int
    repeticiones: int
    pi_promedio: float
    desviacion_pi: float
    error_promedio: float
    error_minimo: float
    error_maximo: float


@dataclass(frozen=True)
class MuestraPuntos:
    """Coordenadas de los puntos generados, solo para graficarlos."""

    x: np.ndarray
    y: np.ndarray
    dentro: np.ndarray

    @property
    def pi_estimado(self) -> float:
        return 4.0 * float(self.dentro.sum()) / len(self.x)


@dataclass(frozen=True)
class FilaComparacion:
    """Resultados de Python y Java para el mismo N."""

    n_puntos: int
    pi_python: float
    pi_java: float
    error_python: float
    error_java: float
    tiempo_python_ms: float
    tiempo_java_ms: float

    @property
    def misma_estimacion(self) -> bool:
        return self.pi_python == self.pi_java

    @property
    def razon_tiempos(self) -> float:
        """Cuántas veces más rápido fue Java (tiempo Python / tiempo Java)."""
        return self.tiempo_python_ms / self.tiempo_java_ms if self.tiempo_java_ms > 0 else float("inf")
