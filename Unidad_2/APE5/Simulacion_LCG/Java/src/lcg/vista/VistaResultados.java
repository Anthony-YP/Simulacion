package lcg.vista;

import java.nio.file.Path;
import java.util.List;

import lcg.modelo.AnalisisEscenario;
import lcg.modelo.AnalisisSecuencia;
import lcg.modelo.Observacion;
import lcg.modelo.ParametrosLCG;
import lcg.modelo.ResultadoCiclo;
import lcg.modelo.ResultadoComparacion;

/**
 * Presenta resultados en forma de texto y tablas.
 *
 * <p>Las vistas se dividen en dos interfaces pequeñas (Segregación de Interfaces):
 * esta, de texto, y {@link VistaGraficos}. El controlador depende de ellas y no
 * de la consola ni de Java2D (Inversión de Dependencias).
 */
public interface VistaResultados {

    /** Encabezado general del programa. */
    void mostrarTitulo(String implementacion);

    /** Separador con el nombre de un paso del procedimiento. */
    void mostrarSeccion(String titulo);

    /** Línea informativa. */
    void mostrarMensaje(String texto);

    /** Parámetros a, c, m, semilla y cantidad de valores. */
    void mostrarParametros(ParametrosLCG parametros, int cantidad);

    /** Tabla n, X(n), U(n). */
    void mostrarObservaciones(List<Observacion> observaciones);

    /** Tabla lado a lado de las primeras {@code filas} posiciones y veredicto global. */
    void mostrarComparacion(ResultadoComparacion resultado, String etiquetaA, String etiquetaB, int filas);

    /**
     * Teorema de Hull-Dobell, repeticiones en la muestra y medición exhaustiva.
     *
     * @param ciclo    medición exhaustiva, o null si no se ejecutó
     * @param segundos duración de la medición exhaustiva
     */
    void mostrarPeriodo(AnalisisSecuencia analisis, ResultadoCiclo ciclo, double segundos);

    /** Comparación del período con parámetros adecuados e inadecuados. */
    void mostrarEscenarios(List<AnalisisEscenario> analisis, int filas);

    /** Estadísticos y período de dos semillas, lado a lado. */
    void mostrarComparacionSemillas(AnalisisSecuencia a, AnalisisSecuencia b);

    /** Aviso de que aún no existen resultados de la otra implementación. */
    void mostrarSinComparacion(String implementacion, Path ruta);

    /** Lista de archivos generados. */
    void mostrarArchivos(List<Path> rutas);
}
