import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.CodeSource;
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
 * Las rutas se calculan a partir de la carpeta Java/ del proyecto, no de la carpeta desde la que se
 * ejecuta. Así los resultados se guardan siempre en Java/Resultados (también con el botón Run del IDE).
 */
public final class Main {

    private static final Path CARPETA_JAVA = ubicarCarpetaJava();
    private static final Path CARPETA_RESULTADOS = CARPETA_JAVA.resolve("Resultados");
    private static final Path RESULTADOS_PYTHON =
            CARPETA_JAVA.getParent().resolve("Python").resolve("Resultados").resolve("resultados_python.csv");

    private Main() {
    }

    /**
     * Busca la carpeta Java/ del proyecto (la que contiene Main.java y montecarlo/).
     * Primero sube desde donde están las clases compiladas (por ejemplo Java/out) y, si no la encuentra,
     * prueba con la carpeta actual y con Simulacion_Monte_Carlo/Java dentro de ella.
     */
    private static Path ubicarCarpetaJava() {
        List<Path> candidatas = new ArrayList<>();
        CodeSource clases = Main.class.getProtectionDomain().getCodeSource();
        if (clases != null) {
            try {
                for (Path p = Path.of(clases.getLocation().toURI()).toAbsolutePath(); p != null; p = p.getParent()) {
                    candidatas.add(p);
                }
            } catch (URISyntaxException | IllegalArgumentException e) {
                // Ubicación no convertible a ruta: se continúa con la carpeta actual.
            }
        }
        Path actual = Path.of("").toAbsolutePath();
        candidatas.add(actual);
        candidatas.add(actual.resolve("Simulacion_Monte_Carlo").resolve("Java"));

        return candidatas.stream()
                .filter(p -> Files.isRegularFile(p.resolve("Main.java")) && Files.isDirectory(p.resolve("montecarlo")))
                .findFirst()
                .orElse(actual);
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
