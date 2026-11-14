package montecarlo.controlador;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import montecarlo.modelo.EstimadorPiMonteCarlo;
import montecarlo.modelo.ExperimentoMonteCarlo;
import montecarlo.modelo.FilaComparacion;
import montecarlo.modelo.GeneradorCongruencialLineal;
import montecarlo.modelo.RepositorioCSV;
import montecarlo.modelo.ResultadoEstimacion;
import montecarlo.modelo.ResumenRepeticiones;
import montecarlo.vista.VistaConsola;
import montecarlo.vista.VistaGraficos;

/** CONTROLADOR: ejecuta las etapas de la simulación en orden y conecta el modelo con la vista. */
public final class ControladorSimulacion {

    private final ConfiguracionSimulacion config;
    private final RepositorioCSV repositorio;
    private final VistaConsola vista;
    private final VistaGraficos graficos;
    private final Path resultadosPython;
    private final EstimadorPiMonteCarlo estimador = new EstimadorPiMonteCarlo();

    public ControladorSimulacion(ConfiguracionSimulacion config, RepositorioCSV repositorio, VistaConsola vista,
                                 VistaGraficos graficos, Path resultadosPython) {
        this.config = config;
        this.repositorio = repositorio;
        this.vista = vista;
        this.graficos = graficos;
        this.resultadosPython = resultadosPython;
    }

    public void ejecutar() {
        ExperimentoMonteCarlo experimento = new ExperimentoMonteCarlo(config.parametros(), estimador);
        List<Path> archivos = new ArrayList<>();

        vista.mostrarEncabezado(config.parametros(), config.lenguaje());
        vista.mostrarMuestraLcg(new GeneradorCongruencialLineal(config.parametros()).generar(config.numerosMuestra()));

        int nCalentamiento = Collections.max(config.tamanios());
        vista.mostrarCalentamiento(nCalentamiento);
        experimento.calentarJit(nCalentamiento);

        // Experimento principal: una ejecución por cada N con la semilla base.
        List<ResultadoEstimacion> resultados = experimento.ejecutarTamanios(config.tamanios());
        vista.mostrarResultados(resultados);
        archivos.add(repositorio.guardarResultados(resultados));

        // Repeticiones: misma N con semillas distintas para analizar la variabilidad del error.
        if (config.repeticiones() > 1) {
            long[] semillas = experimento.semillasRepeticiones(config.repeticiones());
            List<ResumenRepeticiones> resumenes = config.tamanios().stream()
                    .map(n -> experimento.repetir(n, semillas))
                    .toList();
            vista.mostrarRepeticiones(resumenes);
            archivos.add(repositorio.guardarRepeticiones(resumenes));
        }

        // Implementación cruzada: comparar con la versión Python si ya se ejecutó.
        List<FilaComparacion> comparacion =
                FilaComparacion.comparar(resultados, RepositorioCSV.leerResultados(resultadosPython));
        vista.mostrarComparacion(comparacion);
        if (!comparacion.isEmpty()) {
            archivos.add(repositorio.guardarComparacion(comparacion));
        }

        if (config.generarGraficos()) {
            for (int n : config.tamanios()) {
                GeneradorCongruencialLineal generador = new GeneradorCongruencialLineal(config.parametros());
                archivos.add(graficos.graficarPuntos(estimador.muestrearPuntos(generador, n)));
            }
        }

        vista.mostrarArchivos(archivos);
    }
}
