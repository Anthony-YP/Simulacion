package montecarlo.modelo;

/**
 * Método de Monte Carlo para estimar π:  π ≈ 4 · (Nc / N).
 *
 * <p>Lanza N puntos al cuadrado [-1, 1] x [-1, 1] y cuenta los que caen en el círculo inscrito.
 * Cada punto usa dos números consecutivos del LCG: x = 2·U(2i-1) - 1, y = 2·U(2i) - 1.
 */
public final class EstimadorPiMonteCarlo {

    /** Fuente de números en [0, 1). Permite probar el conteo con valores conocidos. */
    @FunctionalInterface
    public interface FuenteUniforme {
        double siguiente();
    }

    /** Devuelve Nc: cantidad de puntos con x² + y² <= 1. */
    public long contarDentro(FuenteUniforme fuente, int nPuntos) {
        if (nPuntos <= 0) {
            throw new IllegalArgumentException("El número de puntos debe ser mayor que 0.");
        }
        long dentro = 0;
        for (int i = 0; i < nPuntos; i++) {
            double x = 2.0 * fuente.siguiente() - 1.0;
            double y = 2.0 * fuente.siguiente() - 1.0;
            if (x * x + y * y <= 1.0) {
                dentro++;
            }
        }
        return dentro;
    }

    public long contarDentro(GeneradorCongruencialLineal generador, int nPuntos) {
        return contarDentro((FuenteUniforme) generador::siguiente, nPuntos);
    }

    public double calcularPi(long puntosDentro, int nPuntos) {
        return 4.0 * puntosDentro / nPuntos;
    }

    public double errorAbsoluto(double piEstimado) {
        return Math.abs(piEstimado - Math.PI);
    }

    /** Genera los mismos puntos que {@link #contarDentro}, guardando sus coordenadas para graficar. */
    public MuestraPuntos muestrearPuntos(GeneradorCongruencialLineal generador, int nPuntos) {
        double[] x = new double[nPuntos];
        double[] y = new double[nPuntos];
        boolean[] dentro = new boolean[nPuntos];
        for (int i = 0; i < nPuntos; i++) {
            x[i] = 2.0 * generador.siguiente() - 1.0;
            y[i] = 2.0 * generador.siguiente() - 1.0;
            dentro[i] = x[i] * x[i] + y[i] * y[i] <= 1.0;
        }
        return new MuestraPuntos(x, y, dentro);
    }
}
