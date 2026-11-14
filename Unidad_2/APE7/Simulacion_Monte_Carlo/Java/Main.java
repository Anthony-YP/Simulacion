import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import montecarlo.controlador.ConfiguracionSimulacion;
import montecarlo.controlador.ControladorSimulacion;
import montecarlo.modelo.ParametrosLCG;
import montecarlo.modelo.RepositorioCSV;
import montecarlo.vista.VistaConsola;
import montecarlo.vista.VistaGraficos;

/**
 * Estimación de π mediante el método de Monte Carlo (versión Java).
 *
 * <pre>
 * java -cp out Main                          Práctica completa (N = 1 000 ... 1 000 000)
 * java -cp out Main --tamanios 1000 10000    Solo algunos tamaños
 * java -cp out Main --semilla 2026           Otra semilla del LCG
 * java -cp out Main --repeticiones 30        Más semillas para analizar el error
 * java -cp out Main --sin-graficos           Solo tablas y CSV
 * </pre>
 *
 * Se ejecuta desde la carpeta Java/, por eso las rutas son relativas a ella.
 */
public final class Main {

    private static final Path CARPETA_RESULTADOS = Path.of("Resultados");
    private static final Path RESULTADOS_PYTHON = Path.of("..", "Python", "Resultados", "resultados_python.csv");

    private Main() {
    }

    public static void main(String[] args) {
        ConfiguracionSimulacion config;
        try {
            config = leerArgumentos(args);
        } catch (IllegalArgumentException e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
            return;
        }
        new ControladorSimulacion(
                config,
                new RepositorioCSV(CARPETA_RESULTADOS, "java"),
                new VistaConsola(),
                new VistaGraficos(CARPETA_RESULTADOS),
                RESULTADOS_PYTHON
        ).ejecutar();
    }

    private static ConfiguracionSimulacion leerArgumentos(String[] args) {
        ConfiguracionSimulacion base = ConfiguracionSimulacion.porDefecto();
        List<Integer> tamanios = base.tamanios();
        ParametrosLCG parametros = base.parametros();
        int repeticiones = base.repeticiones();
        boolean graficos = base.generarGraficos();

        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "--tamanios" -> {
                    List<Integer> leidos = new ArrayList<>();
                    while (i + 1 < args.length && !args[i + 1].startsWith("--")) {
                        int n = entero(args[++i]);
                        if (n <= 0) {
                            throw new IllegalArgumentException("cada N debe ser mayor que 0.");
                        }
                        leidos.add(n);
                    }
                    if (leidos.isEmpty()) {
                        throw new IllegalArgumentException("--tamanios necesita al menos un valor.");
                    }
                    tamanios = List.copyOf(leidos);
                }
                case "--semilla" -> parametros = parametros.conSemilla(entero(valor(args, ++i)));
                case "--repeticiones" -> {
                    repeticiones = entero(valor(args, ++i));
                    if (repeticiones < 1) {
                        throw new IllegalArgumentException("las repeticiones deben ser al menos 1.");
                    }
                }
                case "--sin-graficos" -> graficos = false;
                default -> throw new IllegalArgumentException("opción desconocida: " + args[i]);
            }
        }
        return new ConfiguracionSimulacion(tamanios, parametros, repeticiones, graficos,
                base.numerosMuestra(), base.lenguaje());
    }

    private static String valor(String[] args, int i) {
        if (i >= args.length) {
            throw new IllegalArgumentException("falta el valor de " + args[i - 1]);
        }
        return args[i];
    }

    private static int entero(String texto) {
        try {
            return Integer.parseInt(texto);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("no es un entero válido: " + texto);
        }
    }
}
