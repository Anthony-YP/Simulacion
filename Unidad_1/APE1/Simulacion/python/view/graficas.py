"""VISTA - Gráficas con Matplotlib.

Cada función recibe datos ya calculados y guarda una imagen PNG.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # genera imágenes sin abrir ventanas
import matplotlib.pyplot as plt

from model.clima import ResultadoHora

# Umbrales de la tabla de reglas (se dibujan como franjas de color)
FRANJAS = [
    (0.00, 0.40, "#d9ecd0", "Sin lluvia"),
    (0.40, 0.60, "#fbefc4", "Baja posibilidad"),
    (0.60, 0.75, "#fbd9b5", "Lluvia probable"),
    (0.75, 1.00, "#f6c1c1", "Lluvia"),
]


def _dibujar_franjas(ax) -> None:
    for y0, y1, color, etiqueta in FRANJAS:
        ax.axhspan(y0, y1, color=color, alpha=0.7, label=etiqueta)


def grafica_indice(titulo: str, resultados: list[ResultadoHora], ruta: Path) -> None:
    """Índice I por hora sobre las zonas de la tabla de reglas."""
    horas = [r.hora for r in resultados]
    indices = [r.indice for r in resultados]

    fig, ax = plt.subplots(figsize=(10, 5))
    _dibujar_franjas(ax)
    ax.plot(horas, indices, "o-", color="#1f4e79", linewidth=2, label="Índice I")
    for x, y in zip(horas, indices):
        ax.annotate(f"{y:.3f}", (x, y), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=9)
    ax.set(title=titulo, xlabel="Hora del día", ylabel="Índice I", ylim=(0, 1))
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)


def grafica_variables(resultados: list[ResultadoHora], ruta: Path) -> None:
    """H, N y Tf normalizados: muestra qué variable empuja el índice."""
    horas = [r.hora for r in resultados]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(horas, [r.h for r in resultados], "o-", label="H (humedad)")
    ax.plot(horas, [r.n for r in resultados], "s-", label="N (nubosidad)")
    ax.plot(horas, [r.tf for r in resultados], "^-", label="Tf (factor temperatura)")
    ax.set(title="Variables normalizadas de entrada", xlabel="Hora",
           ylabel="Valor normalizado", ylim=(0, 1.05))
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)


def grafica_comparacion(original: list[ResultadoHora], ajustado: list[ResultadoHora],
                        ruta: Path) -> None:
    """Modelo original vs. ajustado en la misma figura."""
    horas = [r.hora for r in original]
    fig, ax = plt.subplots(figsize=(10, 5))
    _dibujar_franjas(ax)
    ax.plot(horas, [r.indice for r in original], "o-", label="Original (0.5H+0.3N+0.2Tf)")
    ax.plot(horas, [r.indice for r in ajustado], "s-", label="Ajustado (0.45H+0.4N+0.15Tf)")
    ax.set(title="Comparación del modelo original y ajustado", xlabel="Hora",
           ylabel="Índice I", ylim=(0, 1))
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)


def grafica_exponencial(t, curvas: dict[float, object], ruta: Path) -> None:
    """Crecimiento (r > 0) y decrecimiento (r < 0) del modelo P0·e^(rt)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    for r, p in curvas.items():
        if r >= 0:
            ax1.plot(t, p, label=f"r = {r}")
        if r <= 0:
            ax2.plot(t, p, label=f"r = {r}")
    ax1.set(title="Crecimiento exponencial (r ≥ 0)", xlabel="t (horas)", ylabel="P(t)")
    ax2.set(title="Decrecimiento exponencial (r ≤ 0)", xlabel="t (horas)", ylabel="P(t)")
    for ax in (ax1, ax2):
        ax.grid(alpha=0.3)
        ax.legend()
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)
