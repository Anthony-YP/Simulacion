package lcg.modelo;

/**
 * Valores de la recurrencia X(n+1) = (a * X(n) + c) mod m.
 *
 * <p>Es inmutable (record) y se valida al construirse: no puede existir un
 * objeto con parámetros inconsistentes (Responsabilidad Única).
 *
 * @param a       multiplicador, 0 &lt; a &lt; m
 * @param c       incremento, 0 &lt;= c &lt; m
 * @param m       módulo, m &gt;= 2; es la cantidad máxima de valores distintos
 * @param semilla valor inicial X(0), 0 &lt;= X(0) &lt; m
 */
public record ParametrosLCG(long a, long c, long m, long semilla) {

    public ParametrosLCG {
        if (m < 2) {
            throw new IllegalArgumentException("El módulo debe cumplir m >= 2 (m = " + m + ").");
        }
        if (a <= 0 || a >= m) {
            throw new IllegalArgumentException("El multiplicador debe cumplir 0 < a < m (a = " + a + ").");
        }
        if (c < 0 || c >= m) {
            throw new IllegalArgumentException("El incremento debe cumplir 0 <= c < m (c = " + c + ").");
        }
        if (semilla < 0 || semilla >= m) {
            throw new IllegalArgumentException("La semilla debe cumplir 0 <= X(0) < m (X(0) = " + semilla + ").");
        }
        // El mayor valor intermedio posible es a*(m - 1) + c y debe caber en un long de 64 bits;
        // multiplyExact y addExact lanzan ArithmeticException si la operación se desborda.
        try {
            Math.addExact(Math.multiplyExact(a, m - 1), c);
        } catch (ArithmeticException desbordamiento) {
            throw new IllegalArgumentException("a*(m - 1) + c supera 2^63 - 1: no cabe en un long.");
        }
    }

    /** Devuelve una copia con otra semilla (a, c y m no cambian). Se usa en el paso 7. */
    public ParametrosLCG conSemilla(long nuevaSemilla) {
        return new ParametrosLCG(a, c, m, nuevaSemilla);
    }
}
