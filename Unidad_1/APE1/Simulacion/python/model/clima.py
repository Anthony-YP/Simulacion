"""MODELO - Índice de posibilidad de lluvia.

Aquí está toda la lógica matemática del problema

Etapas de la simulación cubiertas en model:
  1. Definición del problema: saber en qué horas del día puede llover.
  2. Formulación conceptual: I = wH*H + wN*N + wT*Tf
  3. Datos: tabla de mediciones de la guía.
  4. Construcción del modelo.
"""

from dataclasses import dataclass

import numpy as np


# ---------------------------------------------------------------------------
# PASO 1 - Definir los parámetros del modelo
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PesosModelo:
    """Pesos de cada variable en el índice. Deben sumar 1 para que I ∈ [0, 1]."""

    nombre: str
    w_humedad: float
    w_nubosidad: float
    w_temperatura: float

    def __post_init__(self) -> None:
        total = self.w_humedad + self.w_nubosidad + self.w_temperatura
        if not np.isclose(total, 1.0):
            raise ValueError(f"Los pesos deben sumar 1 y suman: {total}")


# Modelo original: I = 0.5H + 0.3N + 0.2Tf
MODELO_ORIGINAL = PesosModelo("Original", 0.50, 0.30, 0.20)

# Modelo ajustado: se da más peso a la nubosidad y menos a la temperatura.
# Motivo: con el modelo original las mañanas frías (06:00, 40 % de nubes)
# salen casi siempre como "Lluvia probable" solo por el factor de temperatura, lo cual
# no es tan realista; sin nubes no hay lluvia.

MODELO_AJUSTADO = PesosModelo("Ajustado", 0.45, 0.40, 0.15)

# ---------------------------------------------------------------------------
# PASO 2 - Datos de entrada
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Medicion:
    """La fila de datos medidos: hora, humedad %, nubosidad % y temperatura °C."""

    hora: str
    humedad: float
    nubosidad: float
    temperatura: float


DATOS_GUIA = [
    Medicion("06:00", 65, 40, 14),
    Medicion("08:00", 70, 50, 16),
    Medicion("10:00", 68, 45, 18),
    Medicion("12:00", 60, 30, 22),
    Medicion("14:00", 75, 70, 20),
    Medicion("16:00", 85, 85, 18),
    Medicion("18:00", 92, 95, 16),
    Medicion("20:00", 88, 90, 17),
    Medicion("22:00", 80, 75, 15),
]


# ---------------------------------------------------------------------------
# PASO 3 - Normalización de las variables
# ---------------------------------------------------------------------------

def normalizar(porcentaje: float) -> float:
    """Convierte un porcentaje (0-100) en un valor entre 0 y 1."""
    return porcentaje / 100.0


def factor_temperatura(temperatura: float) -> float:
    """Calcula Tf a partir de la temperatura en °C.

    En la tabla de la guía Tf baja 0.10 cada 2 °C (0.05 por grado) desde
    1.00 a 10 °C hasta 0.10 a 28 °C. Eso es una recta:
        Tf = 1 - 0.05 * (T - 10),  limitada al rango [0.10, 1.00]
    La recta da exactamente los valores de la tabla y además permite
    calcular temperaturas impares como 15 °C o 17 °C (que sí aparecen en los datos).
    """
    tf = 1.0 - 0.05 * (temperatura - 10.0)
    return float(np.clip(tf, 0.10, 1.00))


# ---------------------------------------------------------------------------
# PASO 4 - Ecuación del modelo y reglas de decisión
# ---------------------------------------------------------------------------

def indice_lluvia(h: float, n: float, tf: float, pesos: PesosModelo) -> float:
    """I = wH*H + wN*N + wT*Tf (con los valores ya normalizados)."""
    return pesos.w_humedad * h + pesos.w_nubosidad * n + pesos.w_temperatura * tf


def clasificar(indice: float) -> str:
    """Aplica la tabla de reglas de la guía."""
    if indice < 0.40:
        return "Sin lluvia"
    if indice < 0.60:
        return "Baja posibilidad"
    if indice < 0.75:
        return "Lluvia probable"
    return "Lluvia"


# ---------------------------------------------------------------------------
# PASO 5 - Simulación de todas las horas
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ResultadoHora:
    """Una fila de la tabla final que pide la guía."""

    hora: str
    humedad: float
    nubosidad: float
    temperatura: float
    h: float
    n: float
    tf: float
    indice: float
    estado: str


def simular(datos: list[Medicion], pesos: PesosModelo) -> list[ResultadoHora]:
    """Recorre cada medición, normaliza, calcula I y lo clasifica."""
    resultados = []
    for m in datos:
        h = normalizar(m.humedad)
        n = normalizar(m.nubosidad)
        tf = factor_temperatura(m.temperatura)
        i = indice_lluvia(h, n, tf, pesos)
        resultados.append(
            ResultadoHora(m.hora, m.humedad, m.nubosidad, m.temperatura,
                          h, n, tf, round(i, 4), clasificar(i))
        )
    return resultados
