"""MODELO - Crecimiento y decrecimiento exponencial.

Los resultados esperados y las preguntas de control de la guía hablan de
P0 y de la tasa r, que pertenecen al modelo exponencial:

    P(t) = P0 * e^(r t)

  - P(t): variable dependiente (valor en el tiempo t)
  - t:    variable independiente (horas)
  - P0:   parámetro, valor inicial en t = 0
  - r:    parámetro, tasa de crecimiento (r > 0) o decrecimiento (r < 0)
"""

import numpy as np

# PASO 1 - Parámetros del experimento
P0 = 100.0
TASAS_R = [0.10, 0.05, 0.0, -0.05, -0.10]   # se varía r para ver su influencia
TIEMPO = np.linspace(0, 24, 241)             # 24 horas, cada 0.1 h


# PASO 2 - Ecuación del modelo
def poblacion(t: np.ndarray, p0: float, r: float) -> np.ndarray:
    """Calcula P(t) = P0 * e^(r t) para todos los tiempos a la vez (vectorizado)."""
    return p0 * np.exp(r * t)


# PASO 3 - Experimentación: una curva por cada valor de r
def simular_tasas(t: np.ndarray = TIEMPO, p0: float = P0,
                  tasas: list[float] = TASAS_R) -> dict[float, np.ndarray]:
    """Devuelve {r: P(t)} para cada tasa."""
    return {r: poblacion(t, p0, r) for r in tasas}


def tiempo_duplicacion_o_vida_media(r: float) -> float:
    """Tiempo en que P se duplica (r > 0) o se reduce a la mitad (r < 0): ln2/|r|."""
    if r == 0:
        return float("inf")
    return float(np.log(2) / abs(r))
