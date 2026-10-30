"""Vista de consola: presenta los resultados como texto y tablas ASCII."""

from __future__ import annotations

import os
import sys
from collections.abc import Collection, Sequence
from math import sqrt
from pathlib import Path
from typing import TextIO

from ..modelo import (
    AnalisisEscenario,
    AnalisisSecuencia,
    Observacion,
    ParametrosLCG,
    ResultadoCiclo,
    ResultadoComparacion,
    ResumenEstadistico,
)
from .contratos import VistaResultados


class VistaConsola(VistaResultados):
    """Imprime los resultados en la salida estándar (o en el flujo que se le indique).

    Produce exactamente el mismo texto que la VistaConsola de Java (mismos
    títulos, tablas y número de decimales), de modo que las dos salidas se
    pueden comparar línea por línea.
    """

    ANCHO = 78
    SANGRIA = "  "
    DECIMALES_U = 10

    def __init__(self, salida: TextIO | None = None) -> None:
        # Recibir el flujo permite redirigir la salida, por ejemplo, a un archivo.
        self._salida = salida if salida is not None else sys.stdout

    # ------------------------------------------------------------------ contrato

    def mostrar_titulo(self, implementacion: str) -> None:
        self._imprimir("=" * self.ANCHO)
        self._imprimir(f"{self.SANGRIA}GENERADOR CONGRUENCIAL LINEAL (LCG) - Implementación en {implementacion}")
        self._imprimir(f"{self.SANGRIA}X(n+1) = (a * X(n) + c) mod m          U(n) = X(n) / m")
        self._imprimir("=" * self.ANCHO)

    def mostrar_seccion(self, titulo: str) -> None:
        self._imprimir()
        self._imprimir("-" * self.ANCHO)
        self._imprimir(self.SANGRIA + titulo)
        self._imprimir("-" * self.ANCHO)

    def mostrar_mensaje(self, texto: str) -> None:
        self._imprimir(self.SANGRIA + texto)

    def mostrar_parametros(self, parametros: ParametrosLCG, cantidad: int) -> None:
        self._tabla(
            ("Parámetro", "Descripción", "Valor"),
            [
                ("a", "Multiplicador", str(parametros.a)),
                ("c", "Incremento", str(parametros.c)),
                ("m", "Módulo", self._modulo(parametros.m)),
                ("X(0)", "Semilla", str(parametros.semilla)),
                ("N", "Valores a generar", str(cantidad)),
            ],
            izquierda={0, 1},
        )

    def mostrar_observaciones(self, observaciones: Sequence[Observacion]) -> None:
        self._tabla(
            ("n", "X(n)", "U(n)"),
            [(str(o.n), str(o.x), self._decimal(o.u, self.DECIMALES_U)) for o in observaciones],
        )

    def mostrar_comparacion(
        self, resultado: ResultadoComparacion, etiqueta_a: str, etiqueta_b: str, filas: int
    ) -> None:
        if filas > 0:
            self._tabla(
                ("n", f"X(n) {etiqueta_a}", f"X(n) {etiqueta_b}",
                 f"U(n) {etiqueta_a}", f"U(n) {etiqueta_b}", "¿Coincide?"),
                [
                    (str(f.n), str(f.x_a), str(f.x_b),
                     self._decimal(f.u_a, self.DECIMALES_U), self._decimal(f.u_b, self.DECIMALES_U),
                     "Sí" if f.coincide else "No")
                    for f in resultado.filas[:filas]
                ],
                izquierda={5},
            )
        self.mostrar_mensaje(
            f"{etiqueta_a} vs {etiqueta_b}: {resultado.coincidencias} de {resultado.comparadas} posiciones"
            f" coinciden (longitudes {resultado.longitud_a} y {resultado.longitud_b})."
        )
        self.mostrar_mensaje(
            f"Diferencia máxima en U(n): {self._decimal(resultado.diferencia_maxima_u, self.DECIMALES_U)}"
        )
        if resultado.identicas:
            self.mostrar_mensaje("Veredicto: las secuencias son IDÉNTICAS.")
        elif resultado.primera_discrepancia is None:
            self.mostrar_mensaje("Veredicto: las secuencias son DISTINTAS (tienen longitudes diferentes).")
        else:
            self.mostrar_mensaje(
                f"Veredicto: las secuencias son DISTINTAS (primera diferencia en n = {resultado.primera_discrepancia})."
            )

    def mostrar_periodo(
        self, analisis: AnalisisSecuencia, ciclo: ResultadoCiclo | None, segundos: float | None
    ) -> None:
        p, hd = analisis.parametros, analisis.hull_dobell
        a_menos_1 = p.a - 1
        divisiones = ", ".join(f"{a_menos_1} mod {primo} = {a_menos_1 % primo}" for primo in hd.factores_primos_m)
        self.mostrar_mensaje("Teorema de Hull-Dobell: el período es completo (igual a m) si y solo si")
        self.mostrar_mensaje("se cumplen las tres condiciones siguientes.")
        self._tabla(
            ("#", "Condición", "Verificación", "Resultado"),
            [
                ("1", "mcd(c, m) = 1", f"mcd({p.c}, {p.m}) = {hd.mcd_c_m}",
                 self._cumple(hd.c_coprimo_con_m)),
                ("2", "a - 1 divisible por cada primo de m", divisiones,
                 self._cumple(hd.a_menos_1_divisible_por_primos)),
                ("3", "Si 4 divide a m, 4 divide a a - 1",
                 f"m mod 4 = {p.m % 4}; (a - 1) mod 4 = {a_menos_1 % 4}",
                 self._cumple(hd.a_menos_1_multiplo_de_4)),
            ],
            izquierda={1, 2, 3},
        )
        if hd.periodo_completo:
            self.mostrar_mensaje(f"Período teórico: {p.m} (completo: recorre los m valores antes de repetirse).")
        else:
            self.mostrar_mensaje(f"Período teórico: menor que m = {p.m} (no hay período completo).")

        repeticion = analisis.repeticion
        cantidad = analisis.estadisticas.cantidad
        if repeticion.encontrado:
            self.mostrar_mensaje(
                f"Muestra de {cantidad} valores: X({repeticion.inicio_ciclo + repeticion.periodo}) repite"
                f" a X({repeticion.inicio_ciclo}); período observado = {repeticion.periodo}."
            )
        else:
            porcentaje = self._decimal(100 * cantidad / p.m, 6)
            self.mostrar_mensaje(f"Muestra de {cantidad} valores: ningún valor se repite, el ciclo es mayor que {cantidad}.")
            self.mostrar_mensaje(f"La muestra usa {cantidad} de {p.m} valores del ciclo ({porcentaje} %).")

        if ciclo is None:
            self.mostrar_mensaje("Medición exhaustiva (Brent): no ejecutada; use --periodo-completo.")
        elif ciclo.encontrado:
            self.mostrar_mensaje(
                f"Medición exhaustiva (Brent): período = {ciclo.periodo}, inicio del ciclo = {ciclo.inicio_ciclo}."
            )
            self.mostrar_mensaje(
                f"Evaluaciones de f: {ciclo.pasos}; tiempo: {self._decimal(segundos or 0.0, 2)} s."
            )
        else:
            self.mostrar_mensaje(f"Medición exhaustiva (Brent): el ciclo no se cerró en {ciclo.pasos} evaluaciones.")

    def mostrar_escenarios(self, analisis: Sequence[AnalisisEscenario], filas: int) -> None:
        self.mostrar_mensaje("Escenarios: período con parámetros adecuados e inadecuados.")
        self.mostrar_mensaje("mu = posición donde empieza el ciclo; lambda = longitud del ciclo (período).")
        self._tabla(
            ("Id", "Escenario", "a", "c", "m", "X(0)", "Hull-Dobell", "mu", "lambda"),
            [
                (f"E{i}", item.escenario.nombre, str(item.escenario.parametros.a),
                 str(item.escenario.parametros.c), str(item.escenario.parametros.m),
                 str(item.escenario.parametros.semilla), self._cumple(item.hull_dobell.periodo_completo),
                 self._opcional(item.ciclo.inicio_ciclo), self._opcional(item.ciclo.periodo))
                for i, item in enumerate(analisis, start=1)
            ],
            izquierda={1, 6},
        )
        self.mostrar_mensaje("Primeros valores X(n) de cada escenario (n = 0 es la semilla):")
        cantidad = min([filas, *(len(item.valores) for item in analisis)])
        self._tabla(
            ("n", *(f"E{i}" for i in range(1, len(analisis) + 1))),
            [(str(n), *(str(item.valores[n]) for item in analisis)) for n in range(cantidad)],
        )

    def mostrar_comparacion_semillas(self, a: AnalisisSecuencia, b: AnalisisSecuencia) -> None:
        ea, eb = a.estadisticas, b.estadisticas
        d = self._decimal
        self._tabla(
            ("Estadístico", f"Semilla {a.parametros.semilla}", f"Semilla {b.parametros.semilla}", "Ideal U(0,1)"),
            [
                ("Valores analizados", str(ea.cantidad), str(eb.cantidad), "-"),
                ("Media", d(ea.media, 6), d(eb.media, 6), d(0.5, 6)),
                ("Varianza", d(ea.varianza, 6), d(eb.varianza, 6), d(1 / 12, 6)),
                ("Desviación estándar", d(ea.desviacion_estandar, 6), d(eb.desviacion_estandar, 6), d(sqrt(1 / 12), 6)),
                ("Mínimo", d(ea.minimo, 6), d(eb.minimo, 6), d(0.0, 6)),
                ("Máximo", d(ea.maximo, 6), d(eb.maximo, 6), d(1.0, 6)),
                ("Chi-cuadrado (10 intervalos)", d(ea.chi_cuadrado, 4), d(eb.chi_cuadrado, 4),
                 f"< {d(ea.valor_critico_chi_cuadrado, 3)}"),
                ("Uniformidad (alfa = 0.05)", self._uniformidad(ea), self._uniformidad(eb), "Se acepta"),
                ("Autocorrelación lag 1", d(ea.autocorrelacion_lag1, 6), d(eb.autocorrelacion_lag1, 6), d(0.0, 6)),
                ("Período teórico", self._periodo_teorico(a), self._periodo_teorico(b), "-"),
                ("Valores repetidos en la muestra", self._repetidos(a.repeticion), self._repetidos(b.repeticion),
                 "Ninguno"),
            ],
            izquierda={0},
        )

    def mostrar_sin_comparacion(self, implementacion: str, ruta: Path) -> None:
        """Avisa que todavía no existen resultados de la otra implementación."""
        self.mostrar_mensaje(f"No se encontraron resultados de {implementacion}: {self._ruta_legible(ruta)}")
        self.mostrar_mensaje(f"Ejecute la versión {implementacion} y vuelva a ejecutar este programa para comparar.")

    def mostrar_archivos(self, rutas: Sequence[Path]) -> None:
        self._imprimir()
        self._imprimir("=" * self.ANCHO)
        self.mostrar_mensaje("Archivos generados:")
        for ruta in rutas:
            self.mostrar_mensaje(f"  - {self._ruta_legible(ruta)}")
        self._imprimir("=" * self.ANCHO)

    # ------------------------------------------------------------- utilidades

    def _imprimir(self, texto: str = "") -> None:
        print(texto, file=self._salida)

    def _tabla(
        self, encabezados: Sequence[str], filas: Sequence[Sequence[str]], izquierda: Collection[int] = ()
    ) -> None:
        """Dibuja una tabla con bordes ASCII; cada columna toma el ancho de su celda más larga.

        Las columnas indicadas en `izquierda` se alinean a la izquierda (texto) y el
        resto a la derecha (números), para que las cifras queden encolumnadas.
        """
        anchos = [len(encabezado) for encabezado in encabezados]
        for fila in filas:
            for i, celda in enumerate(fila):
                anchos[i] = max(anchos[i], len(celda))
        borde = "+" + "+".join("-" * (ancho + 2) for ancho in anchos) + "+"
        self._imprimir(self.SANGRIA + borde)
        self._imprimir(
            self.SANGRIA + "|" + "|".join(f" {self._centrar(e, a)} " for e, a in zip(encabezados, anchos)) + "|"
        )
        self._imprimir(self.SANGRIA + borde)
        for fila in filas:
            celdas = (
                f" {celda.ljust(ancho) if i in izquierda else celda.rjust(ancho)} "
                for i, (celda, ancho) in enumerate(zip(fila, anchos))
            )
            self._imprimir(self.SANGRIA + "|" + "|".join(celdas) + "|")
        self._imprimir(self.SANGRIA + borde)

    @staticmethod
    def _centrar(texto: str, ancho: int) -> str:
        # Regla explícita (el espacio sobrante va a la derecha) para que Java la replique igual.
        izquierda = (ancho - len(texto)) // 2
        return " " * izquierda + texto + " " * (ancho - len(texto) - izquierda)

    @staticmethod
    def _decimal(valor: float, decimales: int) -> str:
        # Redondeo "al par" sobre el valor binario exacto; Java usa BigDecimal + HALF_EVEN.
        return f"{valor:.{decimales}f}"

    @staticmethod
    def _modulo(m: int) -> str:
        """Muestra m y, si es potencia de 2, también su exponente (por ejemplo 2^32)."""
        es_potencia_de_2 = m & (m - 1) == 0
        return f"{m} (2^{m.bit_length() - 1})" if es_potencia_de_2 else str(m)

    @staticmethod
    def _cumple(condicion: bool) -> str:
        return "Cumple" if condicion else "No cumple"

    @staticmethod
    def _opcional(valor: int | None) -> str:
        return "-" if valor is None else str(valor)

    @staticmethod
    def _uniformidad(resumen: ResumenEstadistico) -> str:
        return "Se acepta" if resumen.pasa_chi_cuadrado else "Se rechaza"

    @staticmethod
    def _periodo_teorico(analisis: AnalisisSecuencia) -> str:
        m = analisis.parametros.m
        return str(m) if analisis.hull_dobell.periodo_completo else f"< {m}"

    @staticmethod
    def _repetidos(repeticion: ResultadoCiclo) -> str:
        return f"Sí (período {repeticion.periodo})" if repeticion.encontrado else "Ninguno"

    @staticmethod
    def _ruta_legible(ruta: Path) -> str:
        """Ruta relativa al directorio actual, con '/' como separador."""
        try:
            return Path(os.path.relpath(ruta)).as_posix()
        except ValueError:  # en Windows no hay ruta relativa entre unidades distintas
            return str(ruta)
