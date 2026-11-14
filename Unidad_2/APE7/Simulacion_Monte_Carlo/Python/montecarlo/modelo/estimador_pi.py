"""Método de Monte Carlo para estimar π:  π ≈ 4 · (Nc / N)."""
from __future__ import annotations

import math

import numpy as np

from .generador_lcg import GeneradorCongruencialLineal
from .resultados import MuestraPuntos


class EstimadorPiMonteCarlo:
    """Lanza N puntos al cuadrado [-1, 1] x [-1, 1] y cuenta los que caen en el círculo inscrito.

    Cada punto usa dos números consecutivos del LCG:  x = 2·U(2i-1) - 1,  y = 2·U(2i) - 1.
    Área del círculo / área del cuadrado = π / 4, por lo que π ≈ 4 · Nc / N.
    """

    @staticmethod
    def contar_dentro(generador: GeneradorCongruencialLineal, n_puntos: int) -> int:
        """Devuelve Nc: cantidad de puntos con x² + y² <= 1."""
        if n_puntos <= 0:
            raise ValueError("El número de puntos debe ser mayor que 0.")
        siguiente = generador.siguiente  # referencia local: evita buscar el método en cada vuelta
        dentro = 0
        for _ in range(n_puntos):
            x = 2.0 * siguiente() - 1.0
            y = 2.0 * siguiente() - 1.0
            if x * x + y * y <= 1.0:
                dentro += 1
        return dentro

    @staticmethod
    def calcular_pi(puntos_dentro: int, n_puntos: int) -> float:
        return 4.0 * puntos_dentro / n_puntos

    @staticmethod
    def error_absoluto(pi_estimado: float) -> float:
        return abs(pi_estimado - math.pi)

    @staticmethod
    def muestrear_puntos(generador: GeneradorCongruencialLineal, n_puntos: int) -> MuestraPuntos:
        """Genera los mismos puntos que `contar_dentro`, pero guarda sus coordenadas para graficar."""
        numeros = np.array(generador.generar(2 * n_puntos))
        x = 2.0 * numeros[0::2] - 1.0
        y = 2.0 * numeros[1::2] - 1.0
        return MuestraPuntos(x, y, x * x + y * y <= 1.0)
