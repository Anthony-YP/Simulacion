package view;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

import model.ModeloExponencial;
import model.ResultadoHora;

/** VISTA - Tabla en consola y archivo CSV. */
public class VistaConsola {

    public void mostrarTabla(String titulo, List<ResultadoHora> resultados) {
        System.out.println("\n=== " + titulo + " ===");
        System.out.printf("%-6s %5s %5s %4s %5s %5s %5s %7s  %s%n",
                "Hora", "Hum%", "Nub%", "T°C", "H", "N", "Tf", "Índice", "Estado");
        System.out.println("-".repeat(66));
        for (ResultadoHora r : resultados) {
            System.out.printf(Locale.US, "%-6s %5.0f %5.0f %4.0f %5.2f %5.2f %5.2f %7.4f  %s%n",
                    r.hora(), r.humedad(), r.nubosidad(), r.temperatura(),
                    r.h(), r.n(), r.tf(), r.indice(), r.estado());
        }
    }

    public void mostrarHorasLluvia(String titulo, List<ResultadoHora> resultados) {
        String horas = resultados.stream()
                .filter(r -> r.estado().equals("Lluvia probable") || r.estado().equals("Lluvia"))
                .map(ResultadoHora::hora)
                .collect(Collectors.joining(", "));
        System.out.println(titulo + ": posibilidad de lluvia en " + (horas.isEmpty() ? "ninguna hora" : horas));
    }

    public void mostrarTasas() {
        System.out.println("\n=== Modelo exponencial P(t) = P0·e^(rt), P0 = 100 ===");
        System.out.printf("%6s %10s %16s  %s%n", "r", "P(24)", "t dup / t½ (h)", "Comportamiento");
        for (double r : ModeloExponencial.TASAS_R) {
            double pFinal = ModeloExponencial.poblacion(ModeloExponencial.T_MAX, ModeloExponencial.P0, r);
            double t = ModeloExponencial.tiempoDuplicacionOVidaMedia(r);
            String tipo = r > 0 ? "Crecimiento" : r < 0 ? "Decrecimiento" : "Constante";
            String tTxt = Double.isInfinite(t) ? "—" : String.format(Locale.US, "%.2f", t);
            System.out.printf(Locale.US, "%6.2f %10.2f %16s  %s%n", r, pFinal, tTxt, tipo);
        }
    }

    public void guardarCsv(List<ResultadoHora> resultados, Path ruta) throws IOException {
        try (PrintWriter out = new PrintWriter(ruta.toFile(), StandardCharsets.UTF_8)) {
            out.println("Hora,Humedad,Nubosidad,Temp.,H,N,Tf,Índice,Estado");
            for (ResultadoHora r : resultados) {
                out.printf(Locale.US, "%s,%.0f,%.0f,%.0f,%.2f,%.2f,%.2f,%.4f,%s%n",
                        r.hora(), r.humedad(), r.nubosidad(), r.temperatura(),
                        r.h(), r.n(), r.tf(), r.indice(), r.estado());
            }
        }
    }
}
