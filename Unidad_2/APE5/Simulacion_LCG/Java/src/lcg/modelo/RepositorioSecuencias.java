package lcg.modelo;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

/** Contrato de almacenamiento: el controlador no sabe si se usa CSV u otro formato. */
public interface RepositorioSecuencias {

    /** Guarda una secuencia. */
    void guardar(List<Observacion> observaciones, Path ruta) throws IOException;

    /** Lee una secuencia guardada (por esta u otra implementación). */
    List<Observacion> cargar(Path ruta) throws IOException;

    /** Guarda la tabla completa de una comparación. */
    void guardarComparacion(ResultadoComparacion resultado, String etiquetaA, String etiquetaB, Path ruta)
            throws IOException;
}
