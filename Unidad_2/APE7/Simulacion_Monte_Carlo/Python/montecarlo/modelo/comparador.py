"""Empareja los resultados de Python y Java que tienen el mismo N."""
from __future__ import annotations

from collections.abc import Sequence

from .resultados import FilaComparacion, ResultadoEstimacion


def comparar_implementaciones(
    python: Sequence[ResultadoEstimacion], java: Sequence[ResultadoEstimacion]
) -> list[FilaComparacion]:
    java_por_n = {r.n_puntos: r for r in java}
    return [
        FilaComparacion(
            n_puntos=p.n_puntos,
            pi_python=p.pi_estimado,
            pi_java=java_por_n[p.n_puntos].pi_estimado,
            error_python=p.error_absoluto,
            error_java=java_por_n[p.n_puntos].error_absoluto,
            tiempo_python_ms=p.tiempo_ms,
            tiempo_java_ms=java_por_n[p.n_puntos].tiempo_ms,
        )
        for p in python
        if p.n_puntos in java_por_n
    ]
