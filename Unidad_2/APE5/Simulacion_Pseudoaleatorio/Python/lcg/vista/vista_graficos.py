"""Vista gráfica: genera las figuras de la práctica con matplotlib y las guarda en PNG."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

# Se usa Figure directamente (sin pyplot): no abre ventanas ni depende de un
# entorno gráfico, por lo que funciona igual en una terminal o un servidor.
from matplotlib import rc_context
from matplotlib.figure import Figure

from ..modelo import AnalisisEscenario, Observacion, ResumenEstadistico
from .contratos import VistaGraficos

# Paleta sobria: superficie clara, tintas neutras para el texto y colores de serie
# separables también por personas con daltonismo (azul, naranja, aguamarina).
SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_TENUE = "#898781"
CUADRICULA = "#e1e0d9"
EJE = "#c3c2b7"
SERIE_1 = "#2a78d6"
SERIE_2 = "#eb6834"
SERIE_3 = "#1baf7a"

ESTILO = {
    "figure.facecolor": SUPERFICIE,
    "axes.facecolor": SUPERFICIE,
    "savefig.facecolor": SUPERFICIE,
    "axes.edgecolor": EJE,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.axisbelow": True,
    "axes.labelcolor": TINTA_SECUNDARIA,
    "axes.titlecolor": TINTA,
    "axes.titlesize": 10.5,
    "axes.titlelocation": "left",
    "grid.color": CUADRICULA,
    "grid.linewidth": 0.6,
    "grid.linestyle": "-",
    "xtick.color": EJE,
    "ytick.color": EJE,
    "xtick.labelcolor": TINTA_SECUNDARIA,
    "ytick.labelcolor": TINTA_SECUNDARIA,
    "font.size": 9.5,
    "legend.frameon": False,
    "legend.labelcolor": TINTA_SECUNDARIA,
}
PUNTOS_POR_PULGADA = 150


class VistaGraficosMatplotlib(VistaGraficos):
    """Implementación de VistaGraficos basada en matplotlib."""

    def graficar_secuencia(self, observaciones: Sequence[Observacion], titulo: str, ruta: Path) -> Path:
        n = [obs.n for obs in observaciones]
        u = [obs.u for obs in observaciones]
        primeras = min(100, len(observaciones))
        with rc_context(ESTILO):
            figura = Figure(figsize=(10, 6.4), layout="constrained")
            detalle, completa = figura.subplots(2, 1)
            # Arriba: pocas observaciones unidas por líneas para ver los saltos entre valores.
            detalle.plot(n[:primeras], u[:primeras], color=SERIE_1, linewidth=1.1,
                         marker="o", markersize=4, markeredgecolor=SUPERFICIE, markeredgewidth=0.8)
            detalle.set_title(f"Primeras {primeras} observaciones")
            # Abajo: toda la muestra como nube de puntos; si es uniforme, cubre el plano sin huecos.
            completa.scatter(n, u, s=1.5, color=SERIE_1, alpha=0.55, linewidths=0)
            completa.set_title(f"Las {len(observaciones)} observaciones")
            for eje in (detalle, completa):
                eje.set_ylim(0, 1)
                eje.margins(x=0.01)
                eje.set_xlabel("n")
                eje.set_ylabel("U(n)")
            figura.suptitle(titulo, color=TINTA, fontsize=12, fontweight="semibold")
            return self._guardar(figura, ruta)

    def graficar_histograma(self, resumen: ResumenEstadistico, titulo: str, ruta: Path) -> Path:
        k = len(resumen.frecuencias)
        ancho = 1 / k
        esperada = resumen.cantidad / k
        veredicto = "se acepta" if resumen.pasa_chi_cuadrado else "se rechaza"
        with rc_context(ESTILO):
            figura = Figure(figsize=(9, 5.2), layout="constrained")
            eje = figura.subplots()
            # El borde del color de la superficie deja un espacio fino entre barras vecinas.
            barras = eje.bar([(i + 0.5) * ancho for i in range(k)], resumen.frecuencias, width=ancho,
                             color=SERIE_1, edgecolor=SUPERFICIE, linewidth=1.2, label="Frecuencia observada")
            # Etiquetas dentro de la barra: así nunca chocan con la línea de frecuencia esperada.
            eje.bar_label(barras, label_type="center", color="#ffffff", fontsize=9)
            eje.axhline(esperada, color=TINTA, linewidth=1.0, label=f"Frecuencia esperada ({esperada:g})")
            eje.set_xticks([i * ancho for i in range(k + 1)])
            eje.set_xlim(0, 1)
            eje.set_ylim(0, max(*resumen.frecuencias, esperada) * 1.25)
            eje.grid(axis="x", visible=False)
            eje.set_xlabel("Intervalo de U(n)")
            eje.set_ylabel("Frecuencia")
            eje.legend(loc="upper left", ncol=2)
            eje.set_title(
                f"Chi-cuadrado = {resumen.chi_cuadrado:.4f} frente a {resumen.valor_critico_chi_cuadrado} "
                f"(alfa = 0.05, 9 g.l.): la uniformidad {veredicto}"
            )
            figura.suptitle(titulo, color=TINTA, fontsize=12, fontweight="semibold")
            return self._guardar(figura, ruta)

    def graficar_dispersion(self, observaciones: Sequence[Observacion], titulo: str, ruta: Path) -> Path:
        u = [obs.u for obs in observaciones]
        with rc_context(ESTILO):
            figura = Figure(figsize=(6.6, 6.8), layout="constrained")
            eje = figura.subplots()
            # Cada punto es el par (U(n), U(n+1)); patrones visibles indicarían dependencia.
            eje.scatter(u[:-1], u[1:], s=1.5, color=SERIE_1, alpha=0.55, linewidths=0)
            eje.set_xlim(0, 1)
            eje.set_ylim(0, 1)
            eje.set_aspect("equal")
            eje.set_xlabel("U(n)")
            eje.set_ylabel("U(n+1)")
            eje.set_title(f"{len(u) - 1} pares consecutivos")
            figura.suptitle(titulo, color=TINTA, fontsize=12, fontweight="semibold")
            return self._guardar(figura, ruta)

    def graficar_comparacion(
        self,
        a: Sequence[Observacion],
        b: Sequence[Observacion],
        etiqueta_a: str,
        etiqueta_b: str,
        titulo: str,
        ruta: Path,
    ) -> Path:
        pares = list(zip(a, b))
        n = [obs_a.n for obs_a, _ in pares]
        diferencias = [abs(obs_a.u - obs_b.u) for obs_a, obs_b in pares]
        primeras = min(50, len(pares))
        with rc_context(ESTILO):
            figura = Figure(figsize=(10, 6.4), layout="constrained")
            superpuestas, diferencia = figura.subplots(2, 1, height_ratios=(3, 2))
            # Círculos para A y cruces para B: si las secuencias son iguales, cada cruz
            # queda dentro de su círculo; si difieren, se ven dos trazos separados.
            superpuestas.plot(n[:primeras], [obs.u for obs, _ in pares[:primeras]], color=SERIE_1,
                              linewidth=1.1, marker="o", markersize=6, markeredgecolor=SUPERFICIE,
                              markeredgewidth=0.8, label=etiqueta_a)
            superpuestas.plot(n[:primeras], [obs.u for _, obs in pares[:primeras]], color=SERIE_2,
                              linewidth=0.9, marker="x", markersize=5, markeredgewidth=1.3, label=etiqueta_b)
            superpuestas.set_ylim(0, 1.12)
            superpuestas.set_ylabel("U(n)")
            superpuestas.set_title(f"Primeras {primeras} observaciones")
            superpuestas.legend(loc="upper left", ncol=2)
            diferencia.scatter(n, diferencias, s=2, color=SERIE_3, linewidths=0)
            diferencia.set_ylim(-0.05, 1.05)
            diferencia.set_xlabel("n")
            diferencia.set_ylabel("|U_a(n) - U_b(n)|")
            diferencia.set_title(
                f"Diferencia absoluta en las {len(pares)} posiciones (máxima = {max(diferencias, default=0.0):.10f})"
            )
            for eje in (superpuestas, diferencia):
                eje.margins(x=0.01)
            figura.suptitle(titulo, color=TINTA, fontsize=12, fontweight="semibold")
            return self._guardar(figura, ruta)

    def graficar_escenarios(self, analisis: Sequence[AnalisisEscenario], ruta: Path) -> Path:
        with rc_context(ESTILO):
            figura = Figure(figsize=(10, 1.85 * len(analisis) + 0.8), layout="constrained")
            ejes = figura.subplots(len(analisis), 1, sharex=True, squeeze=False)[:, 0]
            for i, (eje, item) in enumerate(zip(ejes, analisis), start=1):
                p, ciclo = item.escenario.parametros, item.ciclo
                n = range(len(item.valores))
                if ciclo.encontrado and ciclo.inicio_ciclo + ciclo.periodo < len(item.valores):
                    # Franja tenue sobre la primera vuelta completa del ciclo.
                    eje.axvspan(ciclo.inicio_ciclo, ciclo.inicio_ciclo + ciclo.periodo, color=SERIE_1,
                                alpha=0.10, linewidth=0)
                eje.plot(n, [x / p.m for x in item.valores], color=SERIE_1, linewidth=1.0,
                         marker="o", markersize=4, markeredgecolor=SUPERFICIE, markeredgewidth=0.8)
                eje.set_ylim(-0.05, 1.05)
                eje.set_yticks((0, 0.5, 1))
                eje.set_ylabel("U(n)")
                periodo = f"λ = {ciclo.periodo}, μ = {ciclo.inicio_ciclo}" if ciclo.encontrado else "ciclo no hallado"
                eje.set_title(f"E{i}. {item.escenario.nombre}  (a = {p.a}, c = {p.c}, m = {p.m}, X(0) = {p.semilla})"
                              f"  ->  {periodo}")
                eje.margins(x=0.01)
            ejes[-1].set_xlabel("n (la franja marca la primera vuelta completa del ciclo)")
            figura.suptitle("Período del LCG con parámetros adecuados e inadecuados", color=TINTA,
                            fontsize=12, fontweight="semibold")
            return self._guardar(figura, ruta)

    @staticmethod
    def _guardar(figura: Figure, ruta: Path) -> Path:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        figura.savefig(ruta, dpi=PUNTOS_POR_PULGADA)
        return ruta
