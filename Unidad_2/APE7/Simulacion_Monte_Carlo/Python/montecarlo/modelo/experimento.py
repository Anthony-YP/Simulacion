"""Ejecución de los experimentos: mide tiempos y resume las repeticiones."""
from __future__ import annotations

import math
import time
from collections.abc import Sequence

import numpy as np

from .estimador_pi import EstimadorPiMonteCarlo
from .generador_lcg import GeneradorCongruencialLineal, ParametrosLCG
from .resultados import ResultadoEstimacion, ResumenRepeticiones

SALTO_SEMILLA = 104_729  # Número primo grande: separa las semillas de cada repetición.


class ExperimentoMonteCarlo:
    """Ejecuta el estimador para distintos tamaños de muestra con un mismo LCG."""

    def __init__(self, parametros: ParametrosLCG, estimador: EstimadorPiMonteCarlo) -> None:
        self._parametros = parametros
        self._estimador = estimador

    def ejecutar(self, n_puntos: int, parametros: ParametrosLCG | None = None) -> ResultadoEstimacion:
        """Una ejecución desde la semilla. El tiempo incluye generar los números y contar los puntos."""
        generador = GeneradorCongruencialLineal(parametros or self._parametros)
        inicio = time.perf_counter()
        dentro = self._estimador.contar_dentro(generador, n_puntos)
        pi_estimado = self._estimador.calcular_pi(dentro, n_puntos)
        tiempo_ms = (time.perf_counter() - inicio) * 1000.0

        error = self._estimador.error_absoluto(pi_estimado)
        return ResultadoEstimacion(n_puntos, dentro, pi_estimado, error, error / math.pi, tiempo_ms)

    def ejecutar_tamanios(self, tamanios: Sequence[int]) -> list[ResultadoEstimacion]:
        return [self.ejecutar(n) for n in tamanios]

    def semillas_repeticiones(self, repeticiones: int) -> list[int]:
        """Semillas X0 + k·SALTO_SEMILLA (k = 1..R), reproducibles e iguales en Java.

        No se usan estados consecutivos del LCG como semillas: la repetición k sería la misma
        secuencia desplazada k posiciones y las estimaciones quedarían casi idénticas.
        """
        m = self._parametros.m
        return [(self._parametros.semilla + k * SALTO_SEMILLA) % m for k in range(1, repeticiones + 1)]

    def repetir(self, n_puntos: int, semillas: Sequence[int]) -> ResumenRepeticiones:
        """Ejecuta el experimento con cada semilla para ver cómo varía el error entre ejecuciones."""
        estimaciones = np.array(
            [self.ejecutar(n_puntos, self._parametros.con_semilla(s)).pi_estimado for s in semillas]
        )
        errores = np.abs(estimaciones - math.pi)
        return ResumenRepeticiones(
            n_puntos=n_puntos,
            repeticiones=len(semillas),
            pi_promedio=float(estimaciones.mean()),
            desviacion_pi=float(estimaciones.std(ddof=1)) if len(semillas) > 1 else 0.0,
            error_promedio=float(errores.mean()),
            error_minimo=float(errores.min()),
            error_maximo=float(errores.max()),
        )
