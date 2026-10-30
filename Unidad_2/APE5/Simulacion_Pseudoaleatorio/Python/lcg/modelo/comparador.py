"""Comparación posición por posición de dos secuencias."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .observacion import Observacion


@dataclass(frozen=True)
class FilaComparacion:
    """Valores de ambas secuencias en una misma posición n."""

    n: int
    x_a: int
    x_b: int
    u_a: float
    u_b: float
    coincide: bool


@dataclass(frozen=True)
class ResultadoComparacion:
    """Filas comparadas y métricas resumen de la comparación."""

    filas: tuple[FilaComparacion, ...]
    longitud_a: int
    longitud_b: int

    @property
    def comparadas(self) -> int:
        return len(self.filas)

    @property
    def coincidencias(self) -> int:
        return sum(1 for fila in self.filas if fila.coincide)

    @property
    def primera_discrepancia(self) -> int | None:
        """Posición n de la primera diferencia, o None si todas coinciden."""
        return next((fila.n for fila in self.filas if not fila.coincide), None)

    @property
    def diferencia_maxima_u(self) -> float:
        return max((abs(fila.u_a - fila.u_b) for fila in self.filas), default=0.0)

    @property
    def identicas(self) -> bool:
        """True solo si ambas secuencias tienen la misma longitud y coinciden en todo."""
        return self.longitud_a == self.longitud_b and self.coincidencias == self.comparadas


class ComparadorSecuencias:
    """Compara dos secuencias valor a valor (X exacto y U con tolerancia configurable).

    La tolerancia por defecto es 0: se exige igualdad exacta, que es lo esperado
    cuando dos implementaciones del mismo algoritmo usan los mismos parámetros.
    """

    def __init__(self, tolerancia_u: float = 0.0) -> None:
        self._tolerancia_u = tolerancia_u

    def comparar(self, a: Sequence[Observacion], b: Sequence[Observacion]) -> ResultadoComparacion:
        # zip recorre hasta la secuencia más corta; la diferencia de longitudes
        # queda registrada en el resultado y hace que `identicas` sea False.
        filas = tuple(
            FilaComparacion(
                n=obs_a.n,
                x_a=obs_a.x,
                x_b=obs_b.x,
                u_a=obs_a.u,
                u_b=obs_b.u,
                coincide=(
                    obs_a.n == obs_b.n
                    and obs_a.x == obs_b.x
                    and abs(obs_a.u - obs_b.u) <= self._tolerancia_u
                ),
            )
            for obs_a, obs_b in zip(a, b)
        )
        return ResultadoComparacion(filas, len(a), len(b))
