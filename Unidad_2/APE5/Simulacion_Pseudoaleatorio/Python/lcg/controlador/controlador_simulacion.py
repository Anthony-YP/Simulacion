"""Controlador: ejecuta los pasos del procedimiento coordinando el modelo y las vistas."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from time import perf_counter

from ..modelo import (
    AnalisisEscenario,
    AnalisisSecuencia,
    AnalizadorEstadistico,
    AnalizadorPeriodo,
    ComparadorSecuencias,
    EscenarioPeriodo,
    GeneradorPseudoaleatorio,
    Observacion,
    ParametrosLCG,
    RepositorioSecuencias,
    ResultadoComparacion,
)
from ..vista import VistaGraficos, VistaResultados
from .configuracion import ConfiguracionSimulacion

# Crea un generador a partir de sus parámetros. Recibirla como dependencia permite
# cambiar de generador sin modificar el controlador (Abierto/Cerrado).
FabricaGenerador = Callable[[ParametrosLCG], GeneradorPseudoaleatorio]


class ControladorSimulacion:
    """Orquesta los 8 pasos de la práctica.

    No hace cálculos ni imprime: pide los datos al modelo y se los entrega a las
    vistas. Todas sus dependencias llegan por el constructor, de modo que pueden
    sustituirse por otras implementaciones de los mismos contratos.
    """

    def __init__(
        self,
        configuracion: ConfiguracionSimulacion,
        fabrica_generador: FabricaGenerador,
        analizador_periodo: AnalizadorPeriodo,
        analizador_estadistico: AnalizadorEstadistico,
        comparador: ComparadorSecuencias,
        repositorio: RepositorioSecuencias,
        vista: VistaResultados,
        graficos: VistaGraficos | None = None,
    ) -> None:
        self._cfg = configuracion
        self._fabrica = fabrica_generador
        self._periodo = analizador_periodo
        self._estadistico = analizador_estadistico
        self._comparador = comparador
        self._repositorio = repositorio
        self._vista = vista
        self._graficos = graficos
        self._archivos: list[Path] = []

    def ejecutar(self) -> None:
        """Ejecuta el procedimiento completo, del paso 1 al 8."""
        cfg = self._cfg
        self._archivos.clear()
        self._vista.mostrar_titulo(cfg.implementacion)

        self._vista.mostrar_seccion("Paso 1. Parámetros del generador")
        self._vista.mostrar_parametros(cfg.parametros, cfg.cantidad)

        base = self._pasos_2_y_3_generacion()
        analisis_base = self._analizar(cfg.parametros, base)
        self._paso_4_primeras_observaciones(base)
        self._paso_5_graficas(base, analisis_base)
        self._paso_6_periodo(analisis_base)
        alternativa = self._paso_7_cambio_de_semilla(base)
        self._paso_8_comparacion(base, analisis_base, alternativa)

        self._vista.mostrar_archivos(self._archivos)

    # ----------------------------------------------------------------- pasos

    def _pasos_2_y_3_generacion(self) -> list[Observacion]:
        cfg = self._cfg
        self._vista.mostrar_seccion(f"Pasos 2 y 3. Generación de {cfg.cantidad} valores en {cfg.implementacion}")
        base = self._generar_y_guardar(cfg.parametros)
        ultimo = base[-1]
        self._vista.mostrar_mensaje(f"Se generaron X(1) ... X({ultimo.n}) con la semilla {cfg.parametros.semilla}.")
        self._vista.mostrar_mensaje(f"Último valor: X({ultimo.n}) = {ultimo.x}  (sirve como control rápido).")
        return base

    def _paso_4_primeras_observaciones(self, base: Sequence[Observacion]) -> None:
        cfg = self._cfg
        self._vista.mostrar_seccion(
            f"Paso 4. Primeras {cfg.filas_tabla} observaciones: {cfg.implementacion} vs {cfg.implementacion_externa}"
        )
        comparacion = self._comparar_con_implementacion_externa(cfg.parametros.semilla)
        if comparacion is None:
            self._vista.mostrar_observaciones(base[: cfg.filas_tabla])
            return
        propia, externa, resultado = comparacion
        self._vista.mostrar_comparacion(resultado, cfg.implementacion, cfg.implementacion_externa, cfg.filas_tabla)
        if self._graficos is not None:
            nombre = f"comparacion_{cfg.implementacion.lower()}_{cfg.implementacion_externa.lower()}.png"
            self._registrar(self._graficos.graficar_comparacion(
                propia, externa, cfg.implementacion, cfg.implementacion_externa,
                f"{cfg.implementacion} vs {cfg.implementacion_externa} con los mismos parámetros "
                f"(semilla {cfg.parametros.semilla})",
                cfg.directorio_resultados / nombre,
            ))

    def _paso_5_graficas(self, base: Sequence[Observacion], analisis: AnalisisSecuencia) -> None:
        cfg = self._cfg
        self._vista.mostrar_seccion("Paso 5. Gráficas de la secuencia")
        if self._graficos is None:
            self._vista.mostrar_mensaje("Gráficas desactivadas.")
            return
        semilla, carpeta = cfg.parametros.semilla, cfg.directorio_resultados
        self._registrar(self._graficos.graficar_secuencia(
            base, f"Secuencia U(n) del LCG (semilla {semilla})", carpeta / f"secuencia_semilla_{semilla}.png"))
        self._registrar(self._graficos.graficar_histograma(
            analisis.estadisticas, f"Histograma de U(n) (semilla {semilla})",
            carpeta / f"histograma_semilla_{semilla}.png"))
        self._registrar(self._graficos.graficar_dispersion(
            base, f"Dispersión U(n) vs U(n+1) (semilla {semilla})", carpeta / f"dispersion_semilla_{semilla}.png"))
        self._vista.mostrar_mensaje("Secuencia U(n) vs n, histograma de frecuencias y dispersión U(n) vs U(n+1).")
        self._vista.mostrar_mensaje("Las rutas de las imágenes aparecen al final, en 'Archivos generados'.")

    def _paso_6_periodo(self, analisis: AnalisisSecuencia) -> None:
        cfg = self._cfg
        self._vista.mostrar_seccion("Paso 6. Análisis del período")
        ciclo, segundos = None, None
        if cfg.periodo_completo:
            transicion = self._fabrica(cfg.parametros).transicion
            inicio = perf_counter()
            ciclo = self._periodo.medir_periodo(transicion, cfg.parametros.semilla)
            segundos = perf_counter() - inicio
        self._vista.mostrar_periodo(analisis, ciclo, segundos)

        escenarios = [self._analizar_escenario(escenario) for escenario in cfg.escenarios]
        if escenarios:
            self._vista.mostrar_escenarios(escenarios, cfg.filas_tabla)
            if self._graficos is not None:
                self._registrar(self._graficos.graficar_escenarios(
                    escenarios, cfg.directorio_resultados / "escenarios_periodo.png"))

    def _paso_7_cambio_de_semilla(self, base: Sequence[Observacion]) -> list[Observacion]:
        cfg = self._cfg
        nuevos = cfg.parametros.con_semilla(cfg.semilla_alternativa)
        self._vista.mostrar_seccion(f"Paso 7. Cambio de semilla: {cfg.parametros.semilla} -> {nuevos.semilla}")
        self._vista.mostrar_mensaje("Se conservan a, c y m; solo cambia el valor inicial X(0).")
        alternativa = self._generar_y_guardar(nuevos)
        self._vista.mostrar_comparacion(
            self._comparador.comparar(base, alternativa),
            f"s={cfg.parametros.semilla}", f"s={nuevos.semilla}", cfg.filas_tabla,
        )
        return alternativa

    def _paso_8_comparacion(
        self, base: Sequence[Observacion], analisis_base: AnalisisSecuencia, alternativa: Sequence[Observacion]
    ) -> None:
        cfg = self._cfg
        nuevos = cfg.parametros.con_semilla(cfg.semilla_alternativa)
        self._vista.mostrar_seccion("Paso 8. Comparación de resultados")

        self._vista.mostrar_mensaje(
            f"8.1 Semilla {cfg.parametros.semilla} frente a semilla {nuevos.semilla} ({cfg.implementacion}):"
        )
        self._vista.mostrar_comparacion_semillas(analisis_base, self._analizar(nuevos, alternativa))
        if self._graficos is not None:
            self._registrar(self._graficos.graficar_comparacion(
                base, alternativa, f"Semilla {cfg.parametros.semilla}", f"Semilla {nuevos.semilla}",
                "Efecto de cambiar la semilla (mismos a, c y m)",
                cfg.directorio_resultados / "comparacion_semillas.png",
            ))

        self._vista.mostrar_mensaje(
            f"8.2 {cfg.implementacion} frente a {cfg.implementacion_externa} con la semilla {nuevos.semilla}:"
        )
        comparacion = self._comparar_con_implementacion_externa(nuevos.semilla)
        if comparacion is not None:
            self._vista.mostrar_comparacion(comparacion[2], cfg.implementacion, cfg.implementacion_externa, 0)

    # ------------------------------------------------------------ auxiliares

    def _generar_y_guardar(self, parametros: ParametrosLCG) -> list[Observacion]:
        """Genera la secuencia de unos parámetros y la guarda en CSV."""
        observaciones = self._fabrica(parametros).generar(self._cfg.cantidad)
        ruta = self._ruta_secuencia(self._cfg.directorio_resultados, self._cfg.implementacion, parametros.semilla)
        self._repositorio.guardar(observaciones, ruta)
        self._registrar(ruta)
        return observaciones

    def _analizar(self, parametros: ParametrosLCG, observaciones: Sequence[Observacion]) -> AnalisisSecuencia:
        """Reúne estadística y período de una secuencia ya generada."""
        return AnalisisSecuencia(
            parametros=parametros,
            estadisticas=self._estadistico.analizar(observaciones),
            hull_dobell=self._periodo.verificar_hull_dobell(parametros),
            repeticion=self._periodo.buscar_repeticion(parametros.semilla, observaciones),
        )

    def _analizar_escenario(self, escenario: EscenarioPeriodo) -> AnalisisEscenario:
        parametros = escenario.parametros
        generador = self._fabrica(parametros)
        valores = (parametros.semilla, *(obs.x for obs in generador.generar(self._cfg.valores_por_escenario - 1)))
        return AnalisisEscenario(
            escenario=escenario,
            hull_dobell=self._periodo.verificar_hull_dobell(parametros),
            ciclo=self._periodo.medir_periodo(generador.transicion, parametros.semilla,
                                              self._cfg.limite_pasos_escenarios),
            valores=valores,
        )

    def _comparar_con_implementacion_externa(
        self, semilla: int
    ) -> tuple[list[Observacion], list[Observacion], ResultadoComparacion] | None:
        """Compara el CSV propio con el de la otra implementación para la misma semilla.

        Se comparan los dos archivos (no la lista en memoria) para que ambos lados
        pasen por el mismo formato y la misma lectura. Devuelve None si no hay datos.
        """
        cfg = self._cfg
        if cfg.directorio_externo is None:
            return None
        ruta_externa = self._ruta_secuencia(cfg.directorio_externo, cfg.implementacion_externa, semilla)
        if not ruta_externa.is_file():
            self._vista.mostrar_sin_comparacion(cfg.implementacion_externa, ruta_externa)
            return None
        propia = self._repositorio.cargar(
            self._ruta_secuencia(cfg.directorio_resultados, cfg.implementacion, semilla))
        externa = self._repositorio.cargar(ruta_externa)
        resultado = self._comparador.comparar(propia, externa)
        nombre = (f"comparacion_{cfg.implementacion.lower()}_{cfg.implementacion_externa.lower()}"
                  f"_semilla_{semilla}.csv")
        ruta_tabla = cfg.directorio_resultados / nombre
        self._repositorio.guardar_comparacion(resultado, cfg.implementacion, cfg.implementacion_externa, ruta_tabla)
        self._registrar(ruta_tabla)
        return propia, externa, resultado

    def _registrar(self, ruta: Path) -> None:
        self._archivos.append(ruta)

    @staticmethod
    def _ruta_secuencia(directorio: Path, implementacion: str, semilla: int) -> Path:
        """Nombre común en ambas implementaciones: secuencia_<lenguaje>_semilla_<semilla>.csv."""
        return directorio / f"secuencia_{implementacion.lower()}_semilla_{semilla}.csv"
