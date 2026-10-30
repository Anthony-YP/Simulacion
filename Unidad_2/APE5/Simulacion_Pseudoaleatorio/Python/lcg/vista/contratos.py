"""Contratos de la capa Vista.

Se separan en dos interfaces pequeñas (Segregación de Interfaces): una vista de
texto no está obligada a dibujar gráficas y viceversa. El controlador depende de
estas abstracciones, no de la consola ni de matplotlib (Inversión de Dependencias).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path

from ..modelo import (
    AnalisisEscenario,
    AnalisisSecuencia,
    Observacion,
    ParametrosLCG,
    ResultadoCiclo,
    ResultadoComparacion,
    ResumenEstadistico,
)


class VistaResultados(ABC):
    """Presenta resultados en forma de texto y tablas."""

    @abstractmethod
    def mostrar_titulo(self, implementacion: str) -> None:
        """Encabezado general del programa."""

    @abstractmethod
    def mostrar_seccion(self, titulo: str) -> None:
        """Separador con el nombre de un paso del procedimiento."""

    @abstractmethod
    def mostrar_mensaje(self, texto: str) -> None:
        """Línea informativa."""

    @abstractmethod
    def mostrar_parametros(self, parametros: ParametrosLCG, cantidad: int) -> None:
        """Parámetros a, c, m, semilla y cantidad de valores."""

    @abstractmethod
    def mostrar_observaciones(self, observaciones: Sequence[Observacion]) -> None:
        """Tabla n, X(n), U(n)."""

    @abstractmethod
    def mostrar_comparacion(
        self, resultado: ResultadoComparacion, etiqueta_a: str, etiqueta_b: str, filas: int
    ) -> None:
        """Tabla lado a lado de las primeras `filas` posiciones y veredicto global."""

    @abstractmethod
    def mostrar_periodo(
        self, analisis: AnalisisSecuencia, ciclo: ResultadoCiclo | None, segundos: float | None
    ) -> None:
        """Teorema de Hull-Dobell, repeticiones en la muestra y medición exhaustiva."""

    @abstractmethod
    def mostrar_escenarios(self, analisis: Sequence[AnalisisEscenario], filas: int) -> None:
        """Comparación del período con parámetros adecuados e inadecuados."""

    @abstractmethod
    def mostrar_comparacion_semillas(self, a: AnalisisSecuencia, b: AnalisisSecuencia) -> None:
        """Estadísticos y período de dos semillas, lado a lado."""

    @abstractmethod
    def mostrar_sin_comparacion(self, implementacion: str, ruta: Path) -> None:
        """Aviso de que aún no existen resultados de la otra implementación."""

    @abstractmethod
    def mostrar_archivos(self, rutas: Sequence[Path]) -> None:
        """Lista de archivos generados."""


class VistaGraficos(ABC):
    """Genera representaciones gráficas y devuelve la ruta del archivo creado."""

    @abstractmethod
    def graficar_secuencia(self, observaciones: Sequence[Observacion], titulo: str, ruta: Path) -> Path:
        """U(n) frente a n."""

    @abstractmethod
    def graficar_histograma(self, resumen: ResumenEstadistico, titulo: str, ruta: Path) -> Path:
        """Frecuencias por intervalo frente a la frecuencia esperada."""

    @abstractmethod
    def graficar_dispersion(self, observaciones: Sequence[Observacion], titulo: str, ruta: Path) -> Path:
        """U(n+1) frente a U(n) para observar dependencia entre valores consecutivos."""

    @abstractmethod
    def graficar_comparacion(
        self,
        a: Sequence[Observacion],
        b: Sequence[Observacion],
        etiqueta_a: str,
        etiqueta_b: str,
        titulo: str,
        ruta: Path,
    ) -> Path:
        """Dos secuencias superpuestas y su diferencia absoluta."""

    @abstractmethod
    def graficar_escenarios(self, analisis: Sequence[AnalisisEscenario], ruta: Path) -> Path:
        """Un panel por escenario para visualizar cada ciclo."""
