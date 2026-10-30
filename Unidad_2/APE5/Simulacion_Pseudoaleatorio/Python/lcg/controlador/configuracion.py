"""Configuración de la simulación: valores de la práctica y escenarios del período."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..modelo import EscenarioPeriodo, ParametrosLCG

# Valores indicados en el procedimiento de la práctica.
A_PRACTICA = 1_664_525
C_PRACTICA = 1_013_904_223
M_PRACTICA = 2**32
SEMILLA_PRACTICA = 12_345
SEMILLA_ALTERNATIVA = 54_321
CANTIDAD_PRACTICA = 10_000
FILAS_TABLA = 20

# E1 cumple el teorema de Hull-Dobell; E2 a E5 incumplen alguna de sus condiciones.
# Con m = 16 el ciclo completo cabe en una tabla y se puede seguir a mano.
ESCENARIOS_PERIODO = (
    EscenarioPeriodo("Cumple Hull-Dobell", ParametrosLCG(a=5, c=3, m=16, semilla=7)),
    EscenarioPeriodo("c par: mcd(c, m) = 2", ParametrosLCG(a=5, c=2, m=16, semilla=7)),
    EscenarioPeriodo("a - 1 no es múltiplo de 4", ParametrosLCG(a=3, c=3, m=16, semilla=7)),
    EscenarioPeriodo("a par", ParametrosLCG(a=4, c=3, m=16, semilla=7)),
    EscenarioPeriodo(
        "a par con m = 2^32",
        ParametrosLCG(a=A_PRACTICA - 1, c=C_PRACTICA, m=M_PRACTICA, semilla=SEMILLA_PRACTICA),
    ),
)


@dataclass(frozen=True)
class ConfiguracionSimulacion:
    """Opciones de una ejecución completa del procedimiento.

    Atributos:
        parametros: a, c, m y semilla del generador principal.
        semilla_alternativa: semilla usada en el paso 7.
        cantidad: valores a generar con cada semilla.
        filas_tabla: filas mostradas en las tablas de consola.
        periodo_completo: si es True, mide el ciclo entero con el algoritmo de Brent.
        directorio_resultados: carpeta donde se guardan CSV y gráficas.
        directorio_externo: carpeta con los CSV de la otra implementación (None = no comparar).
        implementacion / implementacion_externa: nombres usados en archivos y tablas.
        escenarios: parámetros adicionales para estudiar el período.
        valores_por_escenario: valores X(0), X(1), ... registrados por escenario.
        limite_pasos_escenarios: tope de evaluaciones de Brent en cada escenario.
    """

    parametros: ParametrosLCG
    semilla_alternativa: int = SEMILLA_ALTERNATIVA
    cantidad: int = CANTIDAD_PRACTICA
    filas_tabla: int = FILAS_TABLA
    periodo_completo: bool = False
    directorio_resultados: Path = Path("resultados")
    directorio_externo: Path | None = None
    implementacion: str = "Python"
    implementacion_externa: str = "Java"
    escenarios: tuple[EscenarioPeriodo, ...] = ESCENARIOS_PERIODO
    valores_por_escenario: int = 40
    limite_pasos_escenarios: int = 10_000_000

    def __post_init__(self) -> None:
        if self.cantidad < 2:
            raise ValueError("La cantidad de valores debe ser al menos 2.")
        if self.filas_tabla < 0:
            raise ValueError("El número de filas de las tablas no puede ser negativo.")
        # Construir los parámetros alternativos valida la semilla antes de empezar.
        self.parametros.con_semilla(self.semilla_alternativa)
