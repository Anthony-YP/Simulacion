package montecarlo.modelo;

/** Coordenadas de los puntos generados, solo para graficarlos. */
public record MuestraPuntos(double[] x, double[] y, boolean[] dentro) {

    public int cantidad() {
        return x.length;
    }

    public int cantidadDentro() {
        int total = 0;
        for (boolean d : dentro) {
            if (d) {
                total++;
            }
        }
        return total;
    }

    public double piEstimado() {
        return 4.0 * cantidadDentro() / cantidad();
    }
}
