package lcg.modelo;

import java.util.ArrayList;
import java.util.List;

/**
 * Compara dos secuencias valor a valor (X exacto y U con tolerancia configurable).
 *
 * <p>La tolerancia por defecto es 0: se exige igualdad exacta, que es lo esperado
 * cuando dos implementaciones del mismo algoritmo usan los mismos parámetros.
 */
public final class ComparadorSecuencias {

    private final double toleranciaU;

    public ComparadorSecuencias() {
        this(0.0);
    }

    public ComparadorSecuencias(double toleranciaU) {
        this.toleranciaU = toleranciaU;
    }

    public ResultadoComparacion comparar(List<Observacion> a, List<Observacion> b) {
        // Se recorre hasta la secuencia más corta; la diferencia de longitudes queda
        // registrada en el resultado y hace que identicas() sea false.
        int comunes = Math.min(a.size(), b.size());
        List<FilaComparacion> filas = new ArrayList<>(comunes);
        for (int i = 0; i < comunes; i++) {
            Observacion obsA = a.get(i);
            Observacion obsB = b.get(i);
            boolean coincide = obsA.n() == obsB.n()
                    && obsA.x() == obsB.x()
                    && Math.abs(obsA.u() - obsB.u()) <= toleranciaU;
            filas.add(new FilaComparacion(obsA.n(), obsA.x(), obsB.x(), obsA.u(), obsB.u(), coincide));
        }
        return new ResultadoComparacion(filas, a.size(), b.size());
    }
}
