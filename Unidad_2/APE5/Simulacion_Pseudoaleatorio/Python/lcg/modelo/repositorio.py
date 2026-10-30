"""Persistencia de secuencias y comparaciones en archivos CSV."""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path

from .comparador import ResultadoComparacion
from .observacion import Observacion


class RepositorioSecuencias(ABC):
    """Contrato de almacenamiento: el controlador no sabe si se usa CSV u otro formato."""

    @abstractmethod
    def guardar(self, observaciones: Sequence[Observacion], ruta: Path) -> None:
        """Guarda una secuencia."""

    @abstractmethod
    def cargar(self, ruta: Path) -> list[Observacion]:
        """Lee una secuencia guardada (por esta u otra implementación)."""

    @abstractmethod
    def guardar_comparacion(
        self, resultado: ResultadoComparacion, etiqueta_a: str, etiqueta_b: str, ruta: Path
    ) -> None:
        """Guarda la tabla completa de una comparación."""


class RepositorioCSV(RepositorioSecuencias):
    """Lee y escribe el formato CSV compartido con la versión Java: n,X_n,U_n.

    U(n) se escribe con 10 decimales redondeados "al par" sobre el valor binario
    exacto; Java aplica la misma regla (BigDecimal + HALF_EVEN), así que ambos
    archivos son idénticos carácter por carácter cuando las secuencias coinciden.
    """

    ENCABEZADO = ("n", "X_n", "U_n")
    DECIMALES = 10

    def guardar(self, observaciones: Sequence[Observacion], ruta: Path) -> None:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        # newline="" y lineterminator="\n" fijan saltos de línea Unix en cualquier sistema.
        with ruta.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo, lineterminator="\n")
            escritor.writerow(self.ENCABEZADO)
            for obs in observaciones:
                escritor.writerow((obs.n, obs.x, self._decimal(obs.u)))

    def cargar(self, ruta: Path) -> list[Observacion]:
        with ruta.open(newline="", encoding="utf-8") as archivo:
            lector = csv.reader(archivo)
            encabezado = tuple(next(lector, ()))
            if encabezado != self.ENCABEZADO:
                raise ValueError(f"{ruta}: encabezado {encabezado} no es {self.ENCABEZADO}.")
            return [Observacion(int(n), int(x), float(u)) for n, x, u in (fila for fila in lector if fila)]

    def guardar_comparacion(
        self, resultado: ResultadoComparacion, etiqueta_a: str, etiqueta_b: str, ruta: Path
    ) -> None:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with ruta.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo, lineterminator="\n")
            escritor.writerow(
                ("n", f"X_n_{etiqueta_a}", f"X_n_{etiqueta_b}",
                 f"U_n_{etiqueta_a}", f"U_n_{etiqueta_b}", "coincide")
            )
            for fila in resultado.filas:
                escritor.writerow(
                    (fila.n, fila.x_a, fila.x_b, self._decimal(fila.u_a),
                     self._decimal(fila.u_b), "SI" if fila.coincide else "NO")
                )

    def _decimal(self, valor: float) -> str:
        # El formato "f" de Python redondea el valor binario exacto con la regla "al par".
        return f"{valor:.{self.DECIMALES}f}"
