package lcg.controlador;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.function.Function;

import lcg.modelo.AnalisisEscenario;
import lcg.modelo.AnalisisSecuencia;
import lcg.modelo.AnalizadorEstadistico;
import lcg.modelo.AnalizadorPeriodo;
import lcg.modelo.ComparadorSecuencias;
import lcg.modelo.EscenarioPeriodo;
import lcg.modelo.GeneradorPseudoaleatorio;
import lcg.modelo.Observacion;
import lcg.modelo.ParametrosLCG;
import lcg.modelo.RepositorioSecuencias;
import lcg.modelo.ResultadoCiclo;
import lcg.modelo.ResultadoComparacion;
import lcg.vista.VistaGraficos;
import lcg.vista.VistaResultados;

/**
 * Orquesta los 8 pasos de la práctica.
 *
 * <p>No hace cálculos ni imprime: pide los datos al modelo y se los entrega a las
 * vistas. Todas sus dependencias llegan por el constructor, de modo que pueden
 * sustituirse por otras implementaciones de los mismos contratos.
 */
public final class ControladorSimulacion {

    private final ConfiguracionSimulacion cfg;
    /** Crea un generador a partir de sus parámetros; permite cambiar de generador sin tocar esta clase. */
    private final Function<ParametrosLCG, GeneradorPseudoaleatorio> fabrica;
    private final AnalizadorPeriodo periodo;
    private final AnalizadorEstadistico estadistico;
    private final ComparadorSecuencias comparador;
    private final RepositorioSecuencias repositorio;
    private final VistaResultados vista;
    private final VistaGraficos graficos; // null = sin gráficas
    private final List<Path> archivos = new ArrayList<>();

    public ControladorSimulacion(ConfiguracionSimulacion configuracion,
                                 Function<ParametrosLCG, GeneradorPseudoaleatorio> fabricaGenerador,
                                 AnalizadorPeriodo analizadorPeriodo,
                                 AnalizadorEstadistico analizadorEstadistico,
                                 ComparadorSecuencias comparador,
                                 RepositorioSecuencias repositorio,
                                 VistaResultados vista,
                                 VistaGraficos graficos) {
        this.cfg = Objects.requireNonNull(configuracion);
        this.fabrica = Objects.requireNonNull(fabricaGenerador);
        this.periodo = Objects.requireNonNull(analizadorPeriodo);
        this.estadistico = Objects.requireNonNull(analizadorEstadistico);
        this.comparador = Objects.requireNonNull(comparador);
        this.repositorio = Objects.requireNonNull(repositorio);
        this.vista = Objects.requireNonNull(vista);
        this.graficos = graficos;
    }

    /** Ejecuta el procedimiento completo, del paso 1 al 8. */
    public void ejecutar() throws IOException {
        archivos.clear();
        vista.mostrarTitulo(cfg.implementacion());

        vista.mostrarSeccion("Paso 1. Parámetros del generador");
        vista.mostrarParametros(cfg.parametros(), cfg.cantidad());

        List<Observacion> base = pasos2y3Generacion();
        AnalisisSecuencia analisisBase = analizar(cfg.parametros(), base);
        paso4PrimerasObservaciones(base);
        paso5Graficas(base, analisisBase);
        paso6Periodo(analisisBase);
        List<Observacion> alternativa = paso7CambioDeSemilla(base);
        paso8Comparacion(analisisBase, alternativa);

        vista.mostrarArchivos(archivos);
    }

    // ------------------------------------------------------------------- pasos

    private List<Observacion> pasos2y3Generacion() throws IOException {
        vista.mostrarSeccion("Pasos 2 y 3. Generación de " + cfg.cantidad() + " valores en " + cfg.implementacion());
        List<Observacion> base = generarYGuardar(cfg.parametros());
        Observacion ultimo = base.get(base.size() - 1);
        vista.mostrarMensaje("Se generaron X(1) ... X(" + ultimo.n() + ") con la semilla " + cfg.parametros().semilla() + ".");
        vista.mostrarMensaje("Último valor: X(" + ultimo.n() + ") = " + ultimo.x() + "  (sirve como control rápido).");
        return base;
    }

    private void paso4PrimerasObservaciones(List<Observacion> base) throws IOException {
        vista.mostrarSeccion("Paso 4. Primeras " + cfg.filasTabla() + " observaciones: "
                + cfg.implementacion() + " vs " + cfg.implementacionExterna());
        ResultadoComparacion resultado = compararConImplementacionExterna(cfg.parametros().semilla());
        if (resultado == null) {
            vista.mostrarObservaciones(base.subList(0, Math.min(cfg.filasTabla(), base.size())));
        } else {
            vista.mostrarComparacion(resultado, cfg.implementacion(), cfg.implementacionExterna(), cfg.filasTabla());
        }
    }

    private void paso5Graficas(List<Observacion> base, AnalisisSecuencia analisis) throws IOException {
        vista.mostrarSeccion("Paso 5. Gráficas de la secuencia");
        if (graficos == null) {
            vista.mostrarMensaje("Gráficas desactivadas.");
            return;
        }
        long semilla = cfg.parametros().semilla();
        Path carpeta = cfg.directorioResultados();
        archivos.add(graficos.graficarSecuencia(base, "Secuencia U(n) del LCG (semilla " + semilla + ")",
                carpeta.resolve("secuencia_semilla_" + semilla + ".png")));
        archivos.add(graficos.graficarHistograma(analisis.estadisticas(), "Histograma de U(n) (semilla " + semilla + ")",
                carpeta.resolve("histograma_semilla_" + semilla + ".png")));
        archivos.add(graficos.graficarDispersion(base, "Dispersión U(n) vs U(n+1) (semilla " + semilla + ")",
                carpeta.resolve("dispersion_semilla_" + semilla + ".png")));
        vista.mostrarMensaje("Secuencia U(n) vs n, histograma de frecuencias y dispersión U(n) vs U(n+1).");
        vista.mostrarMensaje("Las rutas de las imágenes aparecen al final, en 'Archivos generados'.");
    }

    private void paso6Periodo(AnalisisSecuencia analisis) {
        vista.mostrarSeccion("Paso 6. Análisis del período");
        ResultadoCiclo ciclo = null;
        double segundos = 0.0;
        if (cfg.periodoCompleto()) {
            GeneradorPseudoaleatorio generador = fabrica.apply(cfg.parametros());
            long inicio = System.nanoTime();
            ciclo = periodo.medirPeriodo(generador::transicion, cfg.parametros().semilla());
            segundos = (System.nanoTime() - inicio) / 1e9;
        }
        vista.mostrarPeriodo(analisis, ciclo, segundos);

        List<AnalisisEscenario> escenarios = new ArrayList<>();
        for (EscenarioPeriodo escenario : cfg.escenarios()) {
            escenarios.add(analizarEscenario(escenario));
        }
        if (!escenarios.isEmpty()) {
            vista.mostrarEscenarios(escenarios, cfg.filasTabla());
        }
    }

    private List<Observacion> paso7CambioDeSemilla(List<Observacion> base) throws IOException {
        ParametrosLCG nuevos = cfg.parametros().conSemilla(cfg.semillaAlternativa());
        vista.mostrarSeccion("Paso 7. Cambio de semilla: " + cfg.parametros().semilla() + " -> " + nuevos.semilla());
        vista.mostrarMensaje("Se conservan a, c y m; solo cambia el valor inicial X(0).");
        List<Observacion> alternativa = generarYGuardar(nuevos);
        vista.mostrarComparacion(comparador.comparar(base, alternativa),
                "s=" + cfg.parametros().semilla(), "s=" + nuevos.semilla(), cfg.filasTabla());
        return alternativa;
    }

    private void paso8Comparacion(AnalisisSecuencia analisisBase, List<Observacion> alternativa) throws IOException {
        ParametrosLCG nuevos = cfg.parametros().conSemilla(cfg.semillaAlternativa());
        vista.mostrarSeccion("Paso 8. Comparación de resultados");

        vista.mostrarMensaje("8.1 Semilla " + cfg.parametros().semilla() + " frente a semilla " + nuevos.semilla()
                + " (" + cfg.implementacion() + "):");
        vista.mostrarComparacionSemillas(analisisBase, analizar(nuevos, alternativa));

        vista.mostrarMensaje("8.2 " + cfg.implementacion() + " frente a " + cfg.implementacionExterna()
                + " con la semilla " + nuevos.semilla() + ":");
        ResultadoComparacion resultado = compararConImplementacionExterna(nuevos.semilla());
        if (resultado != null) {
            vista.mostrarComparacion(resultado, cfg.implementacion(), cfg.implementacionExterna(), 0);
        }
    }

    // -------------------------------------------------------------- auxiliares

    /** Genera la secuencia de unos parámetros y la guarda en CSV. */
    private List<Observacion> generarYGuardar(ParametrosLCG parametros) throws IOException {
        List<Observacion> observaciones = fabrica.apply(parametros).generar(cfg.cantidad());
        Path ruta = rutaSecuencia(cfg.directorioResultados(), cfg.implementacion(), parametros.semilla());
        repositorio.guardar(observaciones, ruta);
        archivos.add(ruta);
        return observaciones;
    }

    /** Reúne estadística y período de una secuencia ya generada. */
    private AnalisisSecuencia analizar(ParametrosLCG parametros, List<Observacion> observaciones) {
        return new AnalisisSecuencia(
                parametros,
                estadistico.analizar(observaciones),
                periodo.verificarHullDobell(parametros),
                periodo.buscarRepeticion(parametros.semilla(), observaciones));
    }

    private AnalisisEscenario analizarEscenario(EscenarioPeriodo escenario) {
        ParametrosLCG parametros = escenario.parametros();
        GeneradorPseudoaleatorio generador = fabrica.apply(parametros);
        List<Long> valores = new ArrayList<>();
        valores.add(parametros.semilla());
        for (Observacion obs : generador.generar(cfg.valoresPorEscenario() - 1)) {
            valores.add(obs.x());
        }
        return new AnalisisEscenario(
                escenario,
                periodo.verificarHullDobell(parametros),
                periodo.medirPeriodo(generador::transicion, parametros.semilla(), cfg.limitePasosEscenarios()),
                valores);
    }

    /**
     * Compara el CSV propio con el de la otra implementación para la misma semilla.
     *
     * <p>Se comparan los dos archivos (no la lista en memoria) para que ambos lados
     * pasen por el mismo formato y la misma lectura. Devuelve null si no hay datos.
     */
    private ResultadoComparacion compararConImplementacionExterna(long semilla) throws IOException {
        if (cfg.directorioExterno() == null) {
            return null;
        }
        Path rutaExterna = rutaSecuencia(cfg.directorioExterno(), cfg.implementacionExterna(), semilla);
        if (!Files.isRegularFile(rutaExterna)) {
            vista.mostrarSinComparacion(cfg.implementacionExterna(), rutaExterna);
            return null;
        }
        List<Observacion> propia = repositorio.cargar(
                rutaSecuencia(cfg.directorioResultados(), cfg.implementacion(), semilla));
        List<Observacion> externa = repositorio.cargar(rutaExterna);
        ResultadoComparacion resultado = comparador.comparar(propia, externa);
        Path rutaTabla = cfg.directorioResultados().resolve("comparacion_" + minusculas(cfg.implementacion()) + "_"
                + minusculas(cfg.implementacionExterna()) + "_semilla_" + semilla + ".csv");
        repositorio.guardarComparacion(resultado, cfg.implementacion(), cfg.implementacionExterna(), rutaTabla);
        archivos.add(rutaTabla);
        return resultado;
    }

    /** Nombre común en ambas implementaciones: secuencia_lenguaje_semilla_N.csv. */
    private static Path rutaSecuencia(Path directorio, String implementacion, long semilla) {
        return directorio.resolve("secuencia_" + minusculas(implementacion) + "_semilla_" + semilla + ".csv");
    }

    private static String minusculas(String texto) {
        return texto.toLowerCase(Locale.ROOT);
    }
}
