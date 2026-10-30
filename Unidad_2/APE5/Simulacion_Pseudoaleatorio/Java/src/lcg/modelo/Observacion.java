package lcg.modelo;

/**
 * Un valor de la secuencia.
 *
 * @param n posición dentro de la secuencia (1, 2, 3, ...); X(0) es la semilla
 * @param x entero X(n) producido por la recurrencia
 * @param u valor normalizado U(n) = X(n) / m, perteneciente a [0, 1)
 */
public record Observacion(int n, long x, double u) {
}
