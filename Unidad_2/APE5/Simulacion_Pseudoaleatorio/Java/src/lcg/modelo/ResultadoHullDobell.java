package lcg.modelo;

import java.util.List;

/**
 * Evaluación del teorema de Hull-Dobell.
 *
 * <p>Un LCG mixto tiene período completo (igual a m) si y solo si se cumplen:
 * <ol>
 *   <li>c y m son primos relativos: mcd(c, m) = 1.</li>
 *   <li>a - 1 es divisible por todos los factores primos de m.</li>
 *   <li>Si m es múltiplo de 4, a - 1 también es múltiplo de 4.</li>
 * </ol>
 */
public record ResultadoHullDobell(
        List<Long> factoresPrimosM,
        long mcdCM,
        boolean cCoprimoConM,
        boolean aMenos1DivisiblePorPrimos,
        boolean aMenos1MultiploDe4) {

    public ResultadoHullDobell {
        factoresPrimosM = List.copyOf(factoresPrimosM);
    }

    public boolean periodoCompleto() {
        return cCoprimoConM && aMenos1DivisiblePorPrimos && aMenos1MultiploDe4;
    }
}
