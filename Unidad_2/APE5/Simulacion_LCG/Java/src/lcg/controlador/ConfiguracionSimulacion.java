package lcg.controlador;

import java.nio.file.Path;
import java.util.List;
import java.util.Objects;

import lcg.modelo.EscenarioPeriodo;
import lcg.modelo.ParametrosLCG;

/**
 * Opciones de una ejecución completa del procedimiento.
 *
 * @param parametros            a, c, m y semilla del generador principal
 * @param semillaAlternativa    semilla usada en el paso 7
 * @param cantidad              valores a generar con cada semilla
 * @param filasTabla            filas mostradas en las tablas de consola
 * @param periodoCompleto       si es true, mide el ciclo entero con el algoritmo de Brent
 * @param directorioResultados  carpeta donde se guardan CSV y gráficas
 * @param directorioExterno     carpeta con los CSV de la otra implementación (null = no comparar)
 * @param implementacion        nombre de esta implementación, usado en archivos y tablas
 * @param implementacionExterna nombre de la otra implementación
 * @param escenarios            parámetros adicionales para estudiar el período
 * @param valoresPorEscenario   valores X(0), X(1), ... registrados por escenario
 * @param limitePasosEscenarios tope de evaluaciones de Brent en cada escenario
 */
public record ConfiguracionSimulacion(
        ParametrosLCG parametros,
        long semillaAlternativa,
        int cantidad,
        int filasTabla,
        boolean periodoCompleto,
        Path directorioResultados,
        Path directorioExterno,
        String implementacion,
        String implementacionExterna,
        List<EscenarioPeriodo> escenarios,
        int valoresPorEscenario,
        long limitePasosEscenarios) {

    // Valores indicados en el procedimiento de la práctica.
    public static final long A_PRACTICA = 1_664_525L;
    public static final long C_PRACTICA = 1_013_904_223L;
    public static final long M_PRACTICA = 1L << 32;
    public static final long SEMILLA_PRACTICA = 12_345L;
    public static final long SEMILLA_ALTERNATIVA = 54_321L;
    public static final int CANTIDAD_PRACTICA = 10_000;
    public static final int FILAS_TABLA = 20;

    /**
     * E1 cumple el teorema de Hull-Dobell; E2 a E5 incumplen alguna de sus condiciones.
     * Con m = 16 el ciclo completo cabe en una tabla y se puede seguir a mano.
     */
    public static final List<EscenarioPeriodo> ESCENARIOS_PERIODO = List.of(
            new EscenarioPeriodo("Cumple Hull-Dobell", new ParametrosLCG(5, 3, 16, 7)),
            new EscenarioPeriodo("c par: mcd(c, m) = 2", new ParametrosLCG(5, 2, 16, 7)),
            new EscenarioPeriodo("a - 1 no es múltiplo de 4", new ParametrosLCG(3, 3, 16, 7)),
            new EscenarioPeriodo("a par", new ParametrosLCG(4, 3, 16, 7)),
            new EscenarioPeriodo("a par con m = 2^32",
                    new ParametrosLCG(A_PRACTICA - 1, C_PRACTICA, M_PRACTICA, SEMILLA_PRACTICA)));

    public ConfiguracionSimulacion {
        Objects.requireNonNull(parametros, "parametros");
        Objects.requireNonNull(directorioResultados, "directorioResultados");
        if (cantidad < 2) {
            throw new IllegalArgumentException("La cantidad de valores debe ser al menos 2.");
        }
        if (filasTabla < 0) {
            throw new IllegalArgumentException("El número de filas de las tablas no puede ser negativo.");
        }
        // Construir los parámetros alternativos valida la semilla antes de empezar.
        parametros.conSemilla(semillaAlternativa);
        escenarios = List.copyOf(escenarios);
    }

    /** Configuración de la versión Java con los escenarios y límites por defecto. */
    public static ConfiguracionSimulacion paraJava(ParametrosLCG parametros, long semillaAlternativa, int cantidad,
                                                   int filasTabla, boolean periodoCompleto,
                                                   Path directorioResultados, Path directorioExterno) {
        return new ConfiguracionSimulacion(parametros, semillaAlternativa, cantidad, filasTabla, periodoCompleto,
                directorioResultados, directorioExterno, "Java", "Python", ESCENARIOS_PERIODO, 40, 10_000_000L);
    }
}
