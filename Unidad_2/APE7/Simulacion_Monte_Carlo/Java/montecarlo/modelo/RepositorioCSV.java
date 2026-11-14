package montecarlo.modelo;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

/** Lectura y escritura de resultados en CSV (formato compartido con la versión Python). */
public final class RepositorioCSV {

    private static final String COLUMNAS_RESULTADOS =
            "n_puntos,puntos_dentro,pi_estimado,error_absoluto,error_relativo,tiempo_ms";
    private static final String COLUMNAS_REPETICIONES =
            "n_puntos,repeticiones,pi_promedio,desviacion_pi,error_promedio,error_minimo,error_maximo";
    private static final String COLUMNAS_COMPARACION =
            "n_puntos,pi_java,pi_python,error_java,error_python,tiempo_java_ms,tiempo_python_ms,misma_estimacion";

    private final Path carpeta;
    private final String lenguaje;

    public RepositorioCSV(Path carpeta, String lenguaje) {
        this.carpeta = carpeta;
        this.lenguaje = lenguaje;
    }

    public Path guardarResultados(List<ResultadoEstimacion> resultados) {
        List<String> filas = resultados.stream()
                .map(r -> formato("%d,%d,%.10f,%.10f,%.10f,%.4f", r.nPuntos(), r.puntosDentro(),
                        r.piEstimado(), r.errorAbsoluto(), r.errorRelativo(), r.tiempoMs()))
                .toList();
        return escribir("resultados_" + lenguaje + ".csv", COLUMNAS_RESULTADOS, filas);
    }

    public Path guardarRepeticiones(List<ResumenRepeticiones> resumenes) {
        List<String> filas = resumenes.stream()
                .map(r -> formato("%d,%d,%.10f,%.10f,%.10f,%.10f,%.10f", r.nPuntos(), r.repeticiones(),
                        r.piPromedio(), r.desviacionPi(), r.errorPromedio(), r.errorMinimo(), r.errorMaximo()))
                .toList();
        return escribir("repeticiones_" + lenguaje + ".csv", COLUMNAS_REPETICIONES, filas);
    }

    public Path guardarComparacion(List<FilaComparacion> comparacion) {
        List<String> filas = comparacion.stream()
                .map(f -> formato("%d,%.10f,%.10f,%.10f,%.10f,%.4f,%.4f,%s", f.nPuntos(), f.piJava(),
                        f.piPython(), f.errorJava(), f.errorPython(), f.tiempoJavaMs(), f.tiempoPythonMs(),
                        f.mismaEstimacion() ? "si" : "no"))
                .toList();
        return escribir("comparacion_java_python.csv", COLUMNAS_COMPARACION, filas);
    }

    /** Lee un CSV de resultados (de cualquiera de los dos lenguajes). Devuelve una lista vacía si no existe. */
    public static List<ResultadoEstimacion> leerResultados(Path ruta) {
        if (!Files.exists(ruta)) {
            return List.of();
        }
        try {
            List<String> lineas = Files.readAllLines(ruta, StandardCharsets.UTF_8);
            List<String> columnas = Arrays.asList(lineas.get(0).trim().split(","));
            List<ResultadoEstimacion> resultados = new ArrayList<>();
            for (String linea : lineas.subList(1, lineas.size())) {
                if (linea.isBlank()) {
                    continue;
                }
                String[] v = linea.trim().split(",");
                resultados.add(new ResultadoEstimacion(
                        Integer.parseInt(v[columnas.indexOf("n_puntos")]),
                        Long.parseLong(v[columnas.indexOf("puntos_dentro")]),
                        Double.parseDouble(v[columnas.indexOf("pi_estimado")]),
                        Double.parseDouble(v[columnas.indexOf("error_absoluto")]),
                        Double.parseDouble(v[columnas.indexOf("error_relativo")]),
                        Double.parseDouble(v[columnas.indexOf("tiempo_ms")])));
            }
            return resultados;
        } catch (IOException e) {
            throw new UncheckedIOException("No se pudo leer " + ruta, e);
        }
    }

    private Path escribir(String nombre, String encabezado, List<String> filas) {
        Path ruta = carpeta.resolve(nombre);
        List<String> lineas = new ArrayList<>();
        lineas.add(encabezado);
        lineas.addAll(filas);
        try {
            Files.createDirectories(carpeta);
            Files.write(ruta, lineas, StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new UncheckedIOException("No se pudo escribir " + ruta, e);
        }
        return ruta;
    }

    /** Siempre con punto decimal, sin importar el idioma del sistema (en español sería coma). */
    private static String formato(String plantilla, Object... valores) {
        return String.format(Locale.ROOT, plantilla, valores);
    }
}
