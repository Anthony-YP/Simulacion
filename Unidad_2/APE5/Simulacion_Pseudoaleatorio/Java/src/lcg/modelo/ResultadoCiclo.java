package lcg.modelo;

/**
 * Resultado de buscar el ciclo de una secuencia X(n+1) = f(X(n)).
 *
 * <p>Como f actúa sobre un conjunto finito, tarde o temprano un valor se repite.
 * X(0), ..., X(mu - 1) forman la "cola" previa al ciclo y, desde X(mu), los
 * valores se repiten cada lambda pasos: X(n + lambda) = X(n) para n &gt;= mu.
 *
 * @param encontrado  true si se cerró el ciclo dentro de lo examinado
 * @param periodo     lambda, longitud del ciclo (-1 si no se encontró)
 * @param inicioCiclo mu, posición del primer valor que pertenece al ciclo (-1 si no se encontró)
 * @param pasos       valores examinados o evaluaciones de f realizadas
 */
public record ResultadoCiclo(boolean encontrado, long periodo, long inicioCiclo, long pasos) {

    public static ResultadoCiclo hallado(long periodo, long inicioCiclo, long pasos) {
        return new ResultadoCiclo(true, periodo, inicioCiclo, pasos);
    }

    public static ResultadoCiclo noHallado(long pasos) {
        return new ResultadoCiclo(false, -1, -1, pasos);
    }
}
