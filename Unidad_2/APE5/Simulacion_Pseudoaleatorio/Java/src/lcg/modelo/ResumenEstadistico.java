package lcg.modelo;

import java.util.List;

/**
 * Estadísticos de una muestra U(1), ..., U(N).
 *
 * <p>Valores de referencia para U(0, 1): media 0.5, varianza 1/12 = 0.083333,
 * autocorrelación 0 y chi-cuadrado menor que el valor crítico.
 */
public record ResumenEstadistico(
        int cantidad,
        double media,
        double varianza,
        double minimo,
        double maximo,
        List<Integer> frecuencias,
        double chiCuadrado,
        double valorCriticoChiCuadrado,
        double autocorrelacionLag1) {

    public ResumenEstadistico {
        frecuencias = List.copyOf(frecuencias);
    }

    public double desviacionEstandar() {
        return Math.sqrt(varianza);
    }

    /** true si no hay evidencia (alfa = 0.05) para rechazar la uniformidad. */
    public boolean pasaChiCuadrado() {
        return chiCuadrado < valorCriticoChiCuadrado;
    }
}
