package lcg.modelo;

import java.util.ArrayList;
import java.util.List;

/**
 * Contrato común de cualquier generador pseudoaleatorio.
 *
 * <p>Un generador es una máquina de estados determinista: parte de una semilla,
 * aplica una función de transición X(n+1) = f(X(n)) y normaliza cada estado a
 * U(n) en [0, 1). Los analizadores y el controlador dependen de esta interfaz y
 * no de una clase concreta (Inversión de Dependencias), por lo que se pueden
 * añadir otros generadores sin modificarlos (Abierto/Cerrado).
 */
public interface GeneradorPseudoaleatorio {

    /** Estado inicial X(0). */
    long semilla();

    /** Función pura f: calcula el estado que sigue a {@code x} sin alterar el generador. */
    long transicion(long x);

    /** Convierte un estado entero en un número U en [0, 1). */
    double normalizar(long x);

    /** Avanza un paso la recurrencia y devuelve la nueva observación. */
    Observacion siguiente();

    /** Regresa el generador a la semilla para reproducir la misma secuencia. */
    void reiniciar();

    /** Genera {@code cantidad} observaciones consecutivas a partir del estado actual. */
    default List<Observacion> generar(int cantidad) {
        if (cantidad < 0) {
            throw new IllegalArgumentException("La cantidad de valores a generar no puede ser negativa.");
        }
        List<Observacion> observaciones = new ArrayList<>(cantidad);
        for (int i = 0; i < cantidad; i++) {
            observaciones.add(siguiente());
        }
        return observaciones;
    }
}
