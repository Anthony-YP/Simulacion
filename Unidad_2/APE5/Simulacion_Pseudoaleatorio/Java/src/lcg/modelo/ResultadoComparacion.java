package lcg.modelo;

import java.util.List;
import java.util.OptionalInt;

/** Filas comparadas y métricas resumen de la comparación. */
public record ResultadoComparacion(List<FilaComparacion> filas, int longitudA, int longitudB) {

    public ResultadoComparacion {
        filas = List.copyOf(filas);
    }

    public int comparadas() {
        return filas.size();
    }

    public int coincidencias() {
        return (int) filas.stream().filter(FilaComparacion::coincide).count();
    }

    /** Posición n de la primera diferencia, o vacío si todas coinciden. */
    public OptionalInt primeraDiscrepancia() {
        return filas.stream().filter(fila -> !fila.coincide()).mapToInt(FilaComparacion::n).findFirst();
    }

    public double diferenciaMaximaU() {
        return filas.stream().mapToDouble(fila -> Math.abs(fila.uA() - fila.uB())).max().orElse(0.0);
    }

    /** true solo si ambas secuencias tienen la misma longitud y coinciden en todo. */
    public boolean identicas() {
        return longitudA == longitudB && coincidencias() == comparadas();
    }
}
