package lcg.vista;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

import lcg.modelo.Observacion;
import lcg.modelo.ResumenEstadistico;

/** Genera representaciones gráficas y devuelve la ruta del archivo creado. */
public interface VistaGraficos {

    /** U(n) frente a n. */
    Path graficarSecuencia(List<Observacion> observaciones, String titulo, Path ruta) throws IOException;

    /** Frecuencias por intervalo frente a la frecuencia esperada. */
    Path graficarHistograma(ResumenEstadistico resumen, String titulo, Path ruta) throws IOException;

    /** U(n+1) frente a U(n) para observar dependencia entre valores consecutivos. */
    Path graficarDispersion(List<Observacion> observaciones, String titulo, Path ruta) throws IOException;
}
