"""Gráficas de la simulación con matplotlib (se guardan como PNG)."""
from __future__ import annotations

import math
from collections.abc import Sequence
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Sin ventana: solo se guardan archivos.
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from ..modelo.resultados import (  # noqa: E402
    FilaComparacion,
    MuestraPuntos,
    ResultadoEstimacion,
    ResumenRepeticiones,
)

COLOR_DENTRO = "#2a78c2"
COLOR_FUERA = "#e4572e"
COLOR_PYTHON = "#3572a5"
COLOR_JAVA = "#e76f00"


class VistaGraficos:
    def __init__(self, carpeta: Path) -> None:
        self._carpeta = carpeta

    def graficar_puntos(self, muestra: MuestraPuntos) -> Path:
        """Puntos dentro y fuera del círculo inscrito en el cuadrado."""
        n = len(muestra.x)
        dentro = muestra.dentro
        fig, ax = plt.subplots(figsize=(6.5, 6.5))
        self._dibujar_puntos(ax, muestra.x[dentro], muestra.y[dentro], COLOR_DENTRO, n)
        self._dibujar_puntos(ax, muestra.x[~dentro], muestra.y[~dentro], COLOR_FUERA, n)
        ax.add_patch(plt.Circle((0, 0), 1, fill=False, color="black", linewidth=1.2))
        ax.add_patch(plt.Rectangle((-1, -1), 2, 2, fill=False, color="black", linewidth=1.2))
        ax.set_aspect("equal")
        ax.set_xlim(-1.05, 1.05)
        ax.set_ylim(-1.05, 1.05)
        ax.set_title(f"Monte Carlo con N = {n:,} puntos  →  π ≈ {muestra.pi_estimado:.5f}".replace(",", " "))
        # Leyenda con marcadores de tamaño fijo: con N grande los puntos miden 1 píxel y no se verían.
        ax.legend(handles=[
            Line2D([], [], marker="o", linestyle="none", color=COLOR_DENTRO,
                   label=f"Dentro (Nc = {int(dentro.sum()):,})".replace(",", " ")),
            Line2D([], [], marker="o", linestyle="none", color=COLOR_FUERA,
                   label=f"Fuera ({int((~dentro).sum()):,})".replace(",", " ")),
        ], loc="upper right", framealpha=0.95)
        return self._guardar(fig, f"puntos_monte_carlo_n{n}.png")

    @staticmethod
    def _dibujar_puntos(ax: plt.Axes, x: np.ndarray, y: np.ndarray, color: str, n_total: int) -> None:
        """Marcadores visibles con N pequeño; con N grande, 1 píxel por punto (rápido y sin taparse)."""
        if n_total <= 20_000:
            ax.scatter(x, y, s=6 if n_total <= 2_000 else 1, color=color, linewidths=0)
        else:
            ax.plot(x, y, ",", color=color)

    def graficar_convergencia(
        self, resultados: Sequence[ResultadoEstimacion], resumenes: Sequence[ResumenRepeticiones]
    ) -> Path:
        """π estimado frente a N, con la banda de ±1 desviación estándar de las repeticiones."""
        fig, ax = plt.subplots(figsize=(8, 5))
        if resumenes:
            n = np.array([r.n_puntos for r in resumenes])
            media = np.array([r.pi_promedio for r in resumenes])
            desv = np.array([r.desviacion_pi for r in resumenes])
            ax.fill_between(n, media - desv, media + desv, color=COLOR_DENTRO, alpha=0.18,
                            label=f"Promedio ± 1 desv. ({resumenes[0].repeticiones} semillas)")
            ax.plot(n, media, "--", color=COLOR_DENTRO, linewidth=1)
        ax.plot([r.n_puntos for r in resultados], [r.pi_estimado for r in resultados], "o-",
                color=COLOR_FUERA, label="Ejecución con la semilla base")
        ax.axhline(math.pi, color="black", linewidth=1, label="π real")
        ax.set_xscale("log")
        ax.set_xlabel("Número de puntos N (escala log)")
        ax.set_ylabel("π estimado")
        ax.set_title("Convergencia de la estimación de π")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        return self._guardar(fig, "convergencia_pi.png")

    def graficar_error(
        self, resultados: Sequence[ResultadoEstimacion], resumenes: Sequence[ResumenRepeticiones]
    ) -> Path:
        """Error absoluto frente a N en escala log-log, comparado con la tendencia teórica 1/√N."""
        fig, ax = plt.subplots(figsize=(8, 5))
        n = np.array([r.n_puntos for r in resultados], dtype=float)
        ax.plot(n, [r.error_absoluto for r in resultados], "o-", color=COLOR_FUERA,
                label="Error con la semilla base")
        if resumenes:
            ax.plot([r.n_puntos for r in resumenes], [r.error_promedio for r in resumenes], "s-",
                    color=COLOR_DENTRO, label="Error medio de las repeticiones")
        # Error estándar teórico del estimador: σ = 4·sqrt(p(1-p)/N), con p = π/4.
        p = math.pi / 4
        ax.plot(n, 4 * np.sqrt(p * (1 - p) / n), ":", color="black", label="Error estándar teórico ∝ 1/√N")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Número de puntos N (escala log)")
        ax.set_ylabel("Error absoluto |π̂ − π| (escala log)")
        ax.set_title("Influencia del tamaño de muestra sobre el error")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        return self._guardar(fig, "error_vs_n.png")

    def graficar_tiempos(self, filas: Sequence[FilaComparacion]) -> Path:
        """Barras de tiempo de ejecución de Python y Java para cada N."""
        etiquetas = [f"{f.n_puntos:,}".replace(",", " ") for f in filas]
        posiciones = np.arange(len(filas))
        ancho = 0.38
        fig, ax = plt.subplots(figsize=(8, 5))
        barras_py = ax.bar(posiciones - ancho / 2, [f.tiempo_python_ms for f in filas], ancho,
                           color=COLOR_PYTHON, label="Python")
        barras_java = ax.bar(posiciones + ancho / 2, [f.tiempo_java_ms for f in filas], ancho,
                             color=COLOR_JAVA, label="Java")
        ax.bar_label(barras_py, fmt="%.2f", fontsize=8)
        ax.bar_label(barras_java, fmt="%.2f", fontsize=8)
        ax.set_yscale("log")
        ax.set_xticks(posiciones, etiquetas)
        ax.set_xlabel("Número de puntos N")
        ax.set_ylabel("Tiempo de ejecución en ms (escala log)")
        ax.set_title("Tiempo de ejecución: Python vs Java")
        ax.grid(True, axis="y", which="both", alpha=0.3)
        ax.legend()
        return self._guardar(fig, "comparacion_tiempos_python_java.png")

    def _guardar(self, fig: plt.Figure, nombre: str) -> Path:
        self._carpeta.mkdir(parents=True, exist_ok=True)
        ruta = self._carpeta / nombre
        fig.tight_layout()
        fig.savefig(ruta, dpi=130)
        plt.close(fig)
        return ruta
