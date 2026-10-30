"""Unidad de dato producida por un generador."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Observacion:
    """Un valor de la secuencia.

    Atributos:
        n: posición dentro de la secuencia (1, 2, 3, ...); X(0) es la semilla.
        x: entero X(n) producido por la recurrencia.
        u: valor normalizado U(n) = X(n) / m, perteneciente a [0, 1).
    """

    n: int
    x: int
    u: float
