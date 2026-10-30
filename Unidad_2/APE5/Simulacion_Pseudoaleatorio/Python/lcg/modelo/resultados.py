"""Estructuras que agrupan resultados del modelo para entregarlos juntos a la vista."""

from __future__ import annotations

from dataclasses import dataclass

from .analizador_estadistico import ResumenEstadistico
from .analizador_periodo import ResultadoCiclo, ResultadoHullDobell
from .parametros import ParametrosLCG


@dataclass(frozen=True)
class AnalisisSecuencia:
    """Estadística y período de una secuencia generada con ciertos parámetros."""

    parametros: ParametrosLCG
    estadisticas: ResumenEstadistico
    hull_dobell: ResultadoHullDobell
    repeticion: ResultadoCiclo  # búsqueda de valores repetidos dentro de la muestra


@dataclass(frozen=True)
class EscenarioPeriodo:
    """Conjunto de parámetros con nombre, usado para estudiar cómo cambia el período."""

    nombre: str
    parametros: ParametrosLCG


@dataclass(frozen=True)
class AnalisisEscenario:
    """Resultado de un escenario: teoría, ciclo medido y primeros valores X(0), X(1), ..."""

    escenario: EscenarioPeriodo
    hull_dobell: ResultadoHullDobell
    ciclo: ResultadoCiclo
    valores: tuple[int, ...]
