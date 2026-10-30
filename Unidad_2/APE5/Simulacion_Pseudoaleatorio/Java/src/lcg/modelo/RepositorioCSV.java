package lcg.modelo;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import lcg.util.FormatoDecimal;

/**
 * Lee y escribe el formato CSV compartido con la versión Python: n,X_n,U_n.
 *
 * <p>U(n) se escribe con 10 decimales redondeados "al par" sobre el valor binario
 * exacto (ver {@link FormatoDecimal}), la misma regla que usa Python; por eso
 * ambos archivos son idénticos carácter por carácter cuando las secuencias coinciden.
 */
public final class RepositorioCSV implements RepositorioSecuencias {

    public static final String ENCABEZADO = "n,X_n,U_n";
    public static final int DECIMALES = 10;

    @Override
    public void guardar(List<Observacion> observaciones, Path ruta) throws IOException {
        crearCarpeta(ruta);
        try (BufferedWriter escritor = Files.newBufferedWriter(ruta, StandardCharsets.UTF_8)) {
            // Se escribe "\n" y no newLine(): así el salto de línea es Unix en cualquier sistema.
            escritor.write(ENCABEZADO + "\n");
            for (Observacion obs : observaciones) {
                escritor.write(obs.n() + "," + obs.x() + "," + FormatoDecimal.formatear(obs.u(), DECIMALES) + "\n");
            }
        }
    }

    @Override
    public List<Observacion> cargar(Path ruta) throws IOException {
        List<String> lineas = Files.readAllLines(ruta, StandardCharsets.UTF_8);
        if (lineas.isEmpty() || !lineas.get(0).equals(ENCABEZADO)) {
            throw new IOException(ruta + ": el encabezado no es " + ENCABEZADO + ".");
        }
        List<Observacion> observaciones = new ArrayList<>(lineas.size() - 1);
        for (String linea : lineas.subList(1, lineas.size())) {
            if (linea.isBlank()) {
                continue;
            }
            String[] campos = linea.split(",");
            observaciones.add(new Observacion(
                    Integer.parseInt(campos[0]), Long.parseLong(campos[1]), Double.parseDouble(campos[2])));
        }
        return observaciones;
    }

    @Override
    public void guardarComparacion(ResultadoComparacion resultado, String etiquetaA, String etiquetaB, Path ruta)
            throws IOException {
        crearCarpeta(ruta);
        try (BufferedWriter escritor = Files.newBufferedWriter(ruta, StandardCharsets.UTF_8)) {
            escritor.write("n,X_n_" + etiquetaA + ",X_n_" + etiquetaB + ",U_n_" + etiquetaA + ",U_n_" + etiquetaB
                    + ",coincide\n");
            for (FilaComparacion fila : resultado.filas()) {
                escritor.write(fila.n() + "," + fila.xA() + "," + fila.xB() + ","
                        + FormatoDecimal.formatear(fila.uA(), DECIMALES) + ","
                        + FormatoDecimal.formatear(fila.uB(), DECIMALES) + ","
                        + (fila.coincide() ? "SI" : "NO") + "\n");
            }
        }
    }

    private static void crearCarpeta(Path ruta) throws IOException {
        Path carpeta = ruta.toAbsolutePath().getParent();
        if (carpeta != null) {
            Files.createDirectories(carpeta);
        }
    }
}
