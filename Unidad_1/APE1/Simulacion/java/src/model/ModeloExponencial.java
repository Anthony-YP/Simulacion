package model;

/**
 * MODELO - P(t) = P0 * e^(r t). Crecimiento si r > 0, decrecimiento si r < 0.
 */
public class ModeloExponencial {

    public static final double P0 = 100.0;
    public static final double[] TASAS_R = {0.10, 0.05, 0.0, -0.05, -0.10};
    public static final double T_MAX = 24.0;

    public static double poblacion(double t, double p0, double r) {
        return p0 * Math.exp(r * t);
    }

    /** ln2/|r|: tiempo de duplicación (r > 0) o vida media (r < 0). */
    public static double tiempoDuplicacionOVidaMedia(double r) {
        return r == 0 ? Double.POSITIVE_INFINITY : Math.log(2) / Math.abs(r);
    }
}
