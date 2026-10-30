"""Parámetros que definen un Generador Congruencial Lineal (LCG)."""

from __future__ import annotations

from dataclasses import dataclass, replace

# Mayor entero con signo de 64 bits (el tipo long de Java). Python no tiene este
# límite, pero se aplica igual para que ambas implementaciones acepten exactamente
# los mismos parámetros y nunca se comparen secuencias calculadas de forma distinta.
MAXIMO_ENTERO_64_BITS = 2**63 - 1


@dataclass(frozen=True)
class ParametrosLCG:
    """Valores de la recurrencia X(n+1) = (a * X(n) + c) mod m.

    Es inmutable (frozen) y se valida al construirse: no puede existir un
    objeto con parámetros inconsistentes (Responsabilidad Única).

    Atributos:
        a: multiplicador, 0 < a < m.
        c: incremento, 0 <= c < m.
        m: módulo, m >= 2; es la cantidad máxima de valores distintos.
        semilla: valor inicial X(0), 0 <= X(0) < m.
    """

    a: int
    c: int
    m: int
    semilla: int

    def __post_init__(self) -> None:
        if self.m < 2:
            raise ValueError(f"El módulo debe cumplir m >= 2 (m = {self.m}).")
        if not 0 < self.a < self.m:
            raise ValueError(f"El multiplicador debe cumplir 0 < a < m (a = {self.a}).")
        if not 0 <= self.c < self.m:
            raise ValueError(f"El incremento debe cumplir 0 <= c < m (c = {self.c}).")
        if not 0 <= self.semilla < self.m:
            raise ValueError(f"La semilla debe cumplir 0 <= X(0) < m (X(0) = {self.semilla}).")
        # El mayor valor intermedio posible es a*(m - 1) + c; en Java debe caber en un long.
        if self.a * (self.m - 1) + self.c > MAXIMO_ENTERO_64_BITS:
            raise ValueError("a*(m - 1) + c supera 2^63 - 1: Java no podría calcularlo con long.")

    def con_semilla(self, semilla: int) -> ParametrosLCG:
        """Devuelve una copia con otra semilla (a, c y m no cambian). Se usa en el paso 7."""
        return replace(self, semilla=semilla)
