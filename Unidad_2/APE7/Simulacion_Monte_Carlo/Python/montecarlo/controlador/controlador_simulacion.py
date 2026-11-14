"""CONTROLADOR: ejecuta las etapas de la simulación en orden y conecta el modelo con la vista."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..modelo.comparador import comparar_implementaciones
from ..modelo.estimador_pi import EstimadorPiMonteCarlo
from ..modelo.experimento import ExperimentoMonteCarlo
from ..modelo.generador_lcg import PARAMETROS_NUMERICAL_RECIPES, GeneradorCongruencialLineal, ParametrosLCG
from ..modelo.repositorio_csv import RepositorioCSV
from ..vista.vista_consola import VistaConsola
from ..vista.vista_graficos import VistaGraficos


@dataclass(frozen=True)
class ConfiguracionSimulacion:
    tamanios: tuple[int, ...] = (1_000, 10_000, 100_000, 1_000_000)
    parametros: ParametrosLCG = PARAMETROS_NUMERICAL_RECIPES
    repeticiones: int = 10
    generar_graficos: bool = True
    numeros_muestra: int = 5
    lenguaje: str = "Python"


@dataclass
class ControladorSimulacion:
    configuracion: ConfiguracionSimulacion
    repositorio: RepositorioCSV
    vista: VistaConsola
    graficos: VistaGraficos
    resultados_java: Path
    estimador: EstimadorPiMonteCarlo = field(default_factory=EstimadorPiMonteCarlo)

    def ejecutar(self) -> None:
        config = self.configuracion
        experimento = ExperimentoMonteCarlo(config.parametros, self.estimador)
        archivos: list[Path] = []

        self.vista.mostrar_encabezado(config.parametros, config.lenguaje)
        self.vista.mostrar_muestra_lcg(GeneradorCongruencialLineal(config.parametros).generar(config.numeros_muestra))

        # Experimento principal: una ejecución por cada N con la semilla base.
        resultados = experimento.ejecutar_tamanios(config.tamanios)
        self.vista.mostrar_resultados(resultados)
        archivos.append(self.repositorio.guardar_resultados(resultados))

        # Repeticiones: misma N con semillas distintas para analizar la variabilidad del error.
        resumenes = []
        if config.repeticiones > 1:
            semillas = experimento.semillas_repeticiones(config.repeticiones)
            resumenes = [experimento.repetir(n, semillas) for n in config.tamanios]
            self.vista.mostrar_repeticiones(resumenes)
            archivos.append(self.repositorio.guardar_repeticiones(resumenes))

        # Implementación cruzada: comparar con la versión Java si ya se ejecutó.
        comparacion = comparar_implementaciones(resultados, RepositorioCSV.leer_resultados(self.resultados_java))
        self.vista.mostrar_comparacion(comparacion)
        if comparacion:
            archivos.append(self.repositorio.guardar_comparacion(comparacion))

        if config.generar_graficos:
            for n in config.tamanios:
                muestra = self.estimador.muestrear_puntos(GeneradorCongruencialLineal(config.parametros), n)
                archivos.append(self.graficos.graficar_puntos(muestra))
            archivos.append(self.graficos.graficar_convergencia(resultados, resumenes))
            archivos.append(self.graficos.graficar_error(resultados, resumenes))
            if comparacion:
                archivos.append(self.graficos.graficar_tiempos(comparacion))

        self.vista.mostrar_archivos(archivos)
