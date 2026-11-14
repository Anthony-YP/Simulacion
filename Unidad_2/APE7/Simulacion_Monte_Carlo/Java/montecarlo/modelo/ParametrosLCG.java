package montecarlo.modelo;

/**
 * Parámetros del generador congruencial lineal X(n+1) = (a · X(n) + c) mod m.
 * Se validan al crearse para evitar secuencias degeneradas o desbordamiento de {@code long}.
 */
public record ParametrosLCG(long a, long c, long m, long semilla) {

    /** LCG mixto de Numerical Recipes: cumple Hull-Dobell, período completo 2^32. */
    public static final ParametrosLCG NUMERICAL_RECIPES =
            new ParametrosLCG(1_664_525L, 1_013_904_223L, 1L << 32, 12_345L);

    public ParametrosLCG {
        if (m <= 0) {
            throw new IllegalArgumentException("El módulo m debe ser mayor que 0.");
        }
        if (a <= 0 || a >= m) {
            throw new IllegalArgumentException("El multiplicador a debe cumplir 0 < a < m.");
        }
        if (c < 0 || c >= m) {
            throw new IllegalArgumentException("El incremento c debe cumplir 0 <= c < m.");
        }
        if (semilla < 0 || semilla >= m) {
            throw new IllegalArgumentException("La semilla debe cumplir 0 <= X0 < m.");
        }
        if (c == 0 && semilla == 0) {
            throw new IllegalArgumentException("Con c = 0 la semilla no puede ser 0.");
        }
        // a · (m - 1) + c debe caber en un long para que la aritmética entera sea exacta.
        if (a > (Long.MAX_VALUE - c) / (m - 1 == 0 ? 1 : m - 1)) {
            throw new IllegalArgumentException("a · (m - 1) + c excede el rango de long.");
        }
    }

    /** Mismos parámetros con otra semilla (para repetir el experimento). */
    public ParametrosLCG conSemilla(long nuevaSemilla) {
        return new ParametrosLCG(a, c, m, Math.floorMod(nuevaSemilla, m));
    }
}
