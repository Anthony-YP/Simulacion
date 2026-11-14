"""Generador Congruencial Lineal (LCG): X(n+1) = (a · X(n) + c) mod m,  U(n) = X(n) / m."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParametrosLCG:
    """Parámetros del generador. Se validan al crearse para evitar secuencias degeneradas."""

    a: int
    c: int
    m: int
    semilla: int

    def __post_init__(self) -> None:
        if self.m <= 0:
            raise ValueError("El módulo m debe ser mayor que 0.")
        if not 0 < self.a < self.m:
            raise ValueError("El multiplicador a debe cumplir 0 < a < m.")
        if not 0 <= self.c < self.m:
            raise ValueError("El incremento c debe cumplir 0 <= c < m.")
        if not 0 <= self.semilla < self.m:
            raise ValueError("La semilla debe cumplir 0 <= X0 < m.")
        if self.c == 0 and self.semilla == 0:
            raise ValueError("Con c = 0 la semilla no puede ser 0 (la secuencia sería siempre 0).")

    def con_semilla(self, semilla: int) -> ParametrosLCG:
        """Devuelve los mismos parámetros con otra semilla (para repetir el experimento)."""
        return ParametrosLCG(self.a, self.c, self.m, semilla % self.m)


# LCG mixto de Numerical Recipes: cumple Hull-Dobell, por lo que tiene período completo 2^32.
PARAMETROS_NUMERICAL_RECIPES = ParametrosLCG(a=1_664_525, c=1_013_904_223, m=2**32, semilla=12_345)


class GeneradorCongruencialLineal:
    """Produce números pseudoaleatorios uniformes en [0, 1)."""

    def __init__(self, parametros: ParametrosLCG) -> None:
        self._parametros = parametros
        self._estado = parametros.semilla

    @property
    def parametros(self) -> ParametrosLCG:
        return self._parametros

    @property
    def estado(self) -> int:
        """Último estado entero X(n)."""
        return self._estado

    def siguiente_entero(self) -> int:
        p = self._parametros
        self._estado = (p.a * self._estado + p.c) % p.m
        return self._estado

    def siguiente(self) -> float:
        """Avanza un paso y devuelve U(n) = X(n) / m."""
        return self.siguiente_entero() / self._parametros.m

    def generar(self, cantidad: int) -> list[float]:
        if cantidad < 0:
            raise ValueError("La cantidad de números no puede ser negativa.")
        return [self.siguiente() for _ in range(cantidad)]

    def reiniciar(self) -> None:
        """Vuelve a la semilla para reproducir exactamente la misma secuencia."""
        self._estado = self._parametros.semilla
