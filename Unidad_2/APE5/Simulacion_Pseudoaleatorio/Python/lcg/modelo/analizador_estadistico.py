"""Estadísticos de la secuencia U(n) para contrastarla con la distribución U(0, 1)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import sqrt

from .observacion import Observacion


@dataclass(frozen=True)
class ResumenEstadistico:
    """Estadísticos de una muestra U(1), ..., U(N).

    Valores de referencia para U(0, 1): media 0.5, varianza 1/12 = 0.083333,
    autocorrelación 0 y chi-cuadrado menor que el valor crítico.
    """

    cantidad: int
    media: float
    varianza: float
    minimo: float
    maximo: float
    frecuencias: tuple[int, ...]
    chi_cuadrado: float
    valor_critico_chi_cuadrado: float
    autocorrelacion_lag1: float

    @property
    def desviacion_estandar(self) -> float:
        return sqrt(self.varianza)

    @property
    def pasa_chi_cuadrado(self) -> bool:
        """True si no hay evidencia (alfa = 0.05) para rechazar la uniformidad."""
        return self.chi_cuadrado < self.valor_critico_chi_cuadrado


class AnalizadorEstadistico:
    """Calcula media, varianza, frecuencias, chi-cuadrado y autocorrelación de U(n).

    Todas las sumas usan bucles explícitos y el mismo orden que la versión Java:
    sum() de Python aplica suma compensada desde la versión 3.12, lo que cambiaría
    los últimos decimales y rompería la igualdad exacta entre implementaciones.
    """

    INTERVALOS = 10
    # Valor crítico de tablas chi-cuadrado: alfa = 0.05 y 10 - 1 = 9 grados de libertad.
    VALOR_CRITICO_CHI_CUADRADO = 16.919

    def analizar(self, observaciones: Sequence[Observacion]) -> ResumenEstadistico:
        valores = [obs.u for obs in observaciones]
        n = len(valores)
        if n < 2:
            raise ValueError("Se necesitan al menos 2 observaciones para el análisis.")

        total = 0.0
        for u in valores:
            total += u
        media = total / n

        # Suma de cuadrados de las desviaciones: numerador de la varianza muestral
        # y denominador de la autocorrelación.
        suma_cuadrados = 0.0
        for u in valores:
            desviacion = u - media
            suma_cuadrados += desviacion * desviacion

        # Autocorrelación de retardo 1: relación entre cada U(n) y su sucesor U(n+1).
        suma_productos = 0.0
        for i in range(n - 1):
            suma_productos += (valores[i] - media) * (valores[i + 1] - media)

        frecuencias = self._frecuencias(valores)
        esperada = n / self.INTERVALOS  # frecuencia esperada si la muestra es uniforme
        chi_cuadrado = 0.0
        for observada in frecuencias:
            diferencia = observada - esperada
            chi_cuadrado += diferencia * diferencia / esperada

        return ResumenEstadistico(
            cantidad=n,
            media=media,
            varianza=suma_cuadrados / (n - 1),
            minimo=min(valores),
            maximo=max(valores),
            frecuencias=frecuencias,
            chi_cuadrado=chi_cuadrado,
            valor_critico_chi_cuadrado=self.VALOR_CRITICO_CHI_CUADRADO,
            # Si todos los valores son iguales no hay variación y la autocorrelación no está definida.
            autocorrelacion_lag1=suma_productos / suma_cuadrados if suma_cuadrados > 0 else float("nan"),
        )

    def _frecuencias(self, valores: Sequence[float]) -> tuple[int, ...]:
        """Cuenta cuántos valores caen en cada intervalo [i/k, (i+1)/k)."""
        conteo = [0] * self.INTERVALOS
        for u in valores:
            # min() protege el caso límite en que u * k redondee a k.
            conteo[min(int(u * self.INTERVALOS), self.INTERVALOS - 1)] += 1
        return tuple(conteo)
