package montecarlo.modelo;

/** Una ejecución del experimento con N puntos (una fila de la tabla de la guía). */
public record ResultadoEstimacion(
        int nPuntos,
        long puntosDentro,
        double piEstimado,
        double errorAbsoluto,
        double errorRelativo,
        double tiempoMs) {
}
