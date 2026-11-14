package montecarlo.modelo;

/** Estadísticos de R ejecuciones independientes (semillas distintas) con el mismo N. */
public record ResumenRepeticiones(
        int nPuntos,
        int repeticiones,
        double piPromedio,
        double desviacionPi,
        double errorPromedio,
        double errorMinimo,
        double errorMaximo) {
}
