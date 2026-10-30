"""Generadores de números pseudoaleatorios."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .observacion import Observacion
from .parametros import ParametrosLCG


class GeneradorPseudoaleatorio(ABC):
    """Contrato común de cualquier generador pseudoaleatorio.

    Un generador es una máquina de estados determinista: parte de una semilla,
    aplica una función de transición X(n+1) = f(X(n)) y normaliza cada estado a
    U(n) en [0, 1). Los analizadores y el controlador dependen de esta
    abstracción y no de una clase concreta (Inversión de Dependencias), por lo
    que se pueden añadir otros generadores sin modificarlos (Abierto/Cerrado).
    """

    @property
    @abstractmethod
    def semilla(self) -> int:
        """Estado inicial X(0)."""

    @abstractmethod
    def transicion(self, x: int) -> int:
        """Función pura f: calcula el estado que sigue a `x` sin alterar el generador."""

    @abstractmethod
    def normalizar(self, x: int) -> float:
        """Convierte un estado entero en un número U en [0, 1)."""

    @abstractmethod
    def siguiente(self) -> Observacion:
        """Avanza un paso la recurrencia y devuelve la nueva observación."""

    @abstractmethod
    def reiniciar(self) -> None:
        """Regresa el generador a la semilla para reproducir la misma secuencia."""

    def generar(self, cantidad: int) -> list[Observacion]:
        """Genera `cantidad` observaciones consecutivas a partir del estado actual."""
        if cantidad < 0:
            raise ValueError("La cantidad de valores a generar no puede ser negativa.")
        return [self.siguiente() for _ in range(cantidad)]


class GeneradorCongruencialLineal(GeneradorPseudoaleatorio):
    """Generador Congruencial Lineal mixto: X(n+1) = (a * X(n) + c) mod m."""

    def __init__(self, parametros: ParametrosLCG) -> None:
        self._parametros = parametros
        self._estado = parametros.semilla  # X(n) del último valor generado
        self._n = 0                        # posición n del último valor generado

    @property
    def parametros(self) -> ParametrosLCG:
        return self._parametros

    @property
    def semilla(self) -> int:
        return self._parametros.semilla

    def transicion(self, x: int) -> int:
        p = self._parametros
        # Los enteros de Python tienen precisión arbitraria: a*x + c se calcula sin
        # desbordamiento y luego se reduce módulo m, exactamente como en la fórmula.
        return (p.a * x + p.c) % p.m

    def normalizar(self, x: int) -> float:
        # 0 <= X(n) < m, por lo tanto 0 <= U(n) < 1.
        return x / self._parametros.m

    def siguiente(self) -> Observacion:
        self._estado = self.transicion(self._estado)
        self._n += 1
        return Observacion(self._n, self._estado, self.normalizar(self._estado))

    def reiniciar(self) -> None:
        self._estado = self._parametros.semilla
        self._n = 0
