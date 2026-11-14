package montecarlo.modelo;

import java.util.Arrays;
import java.util.List;
import java.util.stream.LongStream;

/** Ejecuta el estimador para distintos tamaños de muestra, mide tiempos y resume repeticiones. */
public final class ExperimentoMonteCarlo {

    /** Número primo grande que separa las semillas de cada repetición (igual que en Python). */
    public static final long SALTO_SEMILLA = 104_729L;

    private final ParametrosLCG parametros;
    private final EstimadorPiMonteCarlo estimador;

    public ExperimentoMonteCarlo(ParametrosLCG parametros, EstimadorPiMonteCarlo estimador) {
        this.parametros = parametros;
        this.estimador = estimador;
    }

    /**
     * Ejecuta el método una vez sin medir para que el compilador JIT optimice el código.
     * Sin esto, la primera medición incluiría el tiempo de compilación y no sería comparable.
     */
    public void calentarJit(int nPuntos) {
        estimador.contarDentro(new GeneradorCongruencialLineal(parametros), nPuntos);
    }

    public ResultadoEstimacion ejecutar(int nPuntos) {
        return ejecutar(nPuntos, parametros);
    }

    /** Una ejecución desde la semilla. El tiempo incluye generar los números y contar los puntos. */
    public ResultadoEstimacion ejecutar(int nPuntos, ParametrosLCG parametrosEjecucion) {
        GeneradorCongruencialLineal generador = new GeneradorCongruencialLineal(parametrosEjecucion);
        long inicio = System.nanoTime();
        long dentro = estimador.contarDentro(generador, nPuntos);
        double piEstimado = estimador.calcularPi(dentro, nPuntos);
        double tiempoMs = (System.nanoTime() - inicio) / 1_000_000.0;

        double error = estimador.errorAbsoluto(piEstimado);
        return new ResultadoEstimacion(nPuntos, dentro, piEstimado, error, error / Math.PI, tiempoMs);
    }

    public List<ResultadoEstimacion> ejecutarTamanios(List<Integer> tamanios) {
        return tamanios.stream().map(this::ejecutar).toList();
    }

    /**
     * Semillas X0 + k·SALTO_SEMILLA (k = 1..R). No se usan estados consecutivos del LCG:
     * cada repetición sería la misma secuencia desplazada y las estimaciones casi idénticas.
     */
    public long[] semillasRepeticiones(int repeticiones) {
        return LongStream.rangeClosed(1, repeticiones)
                .map(k -> Math.floorMod(parametros.semilla() + k * SALTO_SEMILLA, parametros.m()))
                .toArray();
    }

    /** Ejecuta el experimento con cada semilla para ver cómo varía el error entre ejecuciones. */
    public ResumenRepeticiones repetir(int nPuntos, long[] semillas) {
        double[] estimaciones = Arrays.stream(semillas)
                .mapToDouble(s -> ejecutar(nPuntos, parametros.conSemilla(s)).piEstimado())
                .toArray();
        double[] errores = Arrays.stream(estimaciones).map(estimador::errorAbsoluto).toArray();

        double promedio = Arrays.stream(estimaciones).average().orElse(Double.NaN);
        double sumaCuadrados = Arrays.stream(estimaciones).map(e -> (e - promedio) * (e - promedio)).sum();
        double desviacion = estimaciones.length > 1 ? Math.sqrt(sumaCuadrados / (estimaciones.length - 1)) : 0.0;

        return new ResumenRepeticiones(
                nPuntos,
                semillas.length,
                promedio,
                desviacion,
                Arrays.stream(errores).average().orElse(Double.NaN),
                Arrays.stream(errores).min().orElse(Double.NaN),
                Arrays.stream(errores).max().orElse(Double.NaN));
    }
}
