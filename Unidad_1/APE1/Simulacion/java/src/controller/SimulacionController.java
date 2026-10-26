package controller;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import model.ModeloClima;
import model.PesosModelo;
import model.ResultadoHora;
import view.VistaConsola;
import view.VistaGrafica;

/** CONTROLADOR - Pide los cálculos al modelo y envía los resultados a la vista. */
public class SimulacionController {

    private final Path salida;
    private final VistaConsola consola = new VistaConsola();
    private final VistaGrafica graficas = new VistaGrafica();

    public SimulacionController(Path salida) {
        this.salida = salida;
    }

    public void ejecutar() throws IOException {
        // PASO 1 - Carpeta de resultados
        Files.createDirectories(salida);

        // PASO 2 - Simular modelo original y ajustado
        List<ResultadoHora> original = ModeloClima.simular(ModeloClima.DATOS_GUIA, PesosModelo.ORIGINAL);
        List<ResultadoHora> ajustado = ModeloClima.simular(ModeloClima.DATOS_GUIA, PesosModelo.AJUSTADO);

        // PASO 3 - Tablas en consola y CSV
        consola.mostrarTabla("Modelo original: I = 0.5H + 0.3N + 0.2Tf", original);
        consola.mostrarTabla("Modelo ajustado: I = 0.45H + 0.40N + 0.15Tf", ajustado);
        System.out.println();
        consola.mostrarHorasLluvia("Original", original);
        consola.mostrarHorasLluvia("Ajustado", ajustado);
        consola.guardarCsv(original, salida.resolve("tabla_original.csv"));
        consola.guardarCsv(ajustado, salida.resolve("tabla_ajustada.csv"));

        // PASO 4 - Gráficas del índice
        graficas.graficaIndice("Índice de lluvia - modelo original", List.of(original),
                List.of("Original"), salida.resolve("indice_original.png"));
        graficas.graficaIndice("Índice de lluvia - modelo ajustado", List.of(ajustado),
                List.of("Ajustado"), salida.resolve("indice_ajustado.png"));
        graficas.graficaIndice("Comparación original vs. ajustado", List.of(original, ajustado),
                List.of("Original", "Ajustado"), salida.resolve("comparacion.png"));

        // PASO 5 - Modelo exponencial: influencia de r
        consola.mostrarTasas();
        graficas.graficaExponencial(salida.resolve("exponencial.png"));

        System.out.println("\nResultados guardados en: " + salida.toAbsolutePath());
    }
}
