package lcg;

import java.io.IOException;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import lcg.controlador.ConfiguracionSimulacion;
import lcg.controlador.ControladorSimulacion;
import lcg.modelo.AnalizadorEstadistico;
import lcg.modelo.AnalizadorPeriodo;
import lcg.modelo.ComparadorSecuencias;
import lcg.modelo.GeneradorCongruencialLineal;
import lcg.modelo.ParametrosLCG;
import lcg.modelo.RepositorioCSV;
import lcg.vista.VistaConsola;
import lcg.vista.VistaGraficosJava2D;

/**
 * Punto de entrada de la versión Java del Generador Congruencial Lineal.
 *
 * <p>Es la "raíz de composición": aquí, y solo aquí, se crean las clases concretas
 * del modelo y de las vistas, que luego se inyectan al controlador. Las opciones
 * son las mismas que las de la versión Python. Debe ejecutarse desde la carpeta Java.
 */
public final class Main {

    private static final Set<String> BANDERAS = Set.of("--periodo-completo", "--sin-graficas", "--help", "-h");
    private static final Set<String> OPCIONES_CON_VALOR = Set.of("--a", "--c", "--m", "--semilla",
            "--semilla-alternativa", "--n", "--filas", "--resultados", "--comparar-con");

    private static final String AYUDA = """
            Uso: java -cp out lcg.Main [opciones]

            Generador Congruencial Lineal: X(n+1) = (a*X(n) + c) mod m,  U(n) = X(n)/m.

            Opciones:
              --a N                    multiplicador (defecto: 1664525)
              --c N                    incremento (defecto: 1013904223)
              --m N                    módulo (defecto: 2^32 = 4294967296)
              --semilla N              semilla X(0) (defecto: 12345)
              --semilla-alternativa N  semilla del paso 7 (defecto: 54321)
              --n N                    valores a generar (defecto: 10000)
              --filas N                filas de las tablas de consola (defecto: 20)
              --periodo-completo       mide el ciclo completo con el algoritmo de Brent
              --resultados RUTA        carpeta de salida (defecto: resultados)
              --comparar-con RUTA      carpeta con los CSV de la versión Python (defecto: ../Python/resultados)
              --sin-graficas           omite las gráficas
              -h, --help               muestra esta ayuda
            """;

    private Main() {
    }

    public static void main(String[] args) {
        // Modo sin pantalla: las gráficas se dibujan en memoria y se guardan como PNG.
        System.setProperty("java.awt.headless", "true");
        try {
            Map<String, String> opciones = leerOpciones(args);
            if (opciones.containsKey("--help") || opciones.containsKey("-h")) {
                System.out.print(AYUDA);
                return;
            }
            crearControlador(opciones).ejecutar();
        } catch (IllegalArgumentException error) {
            System.err.println("Error: " + error.getMessage());
            System.err.println("Use --help para ver las opciones.");
            System.exit(2);
        } catch (IOException error) {
            System.err.println("Error de archivo: " + error.getMessage());
            System.exit(1);
        }
    }

    /** Ensambla el controlador con las implementaciones concretas (inyección de dependencias). */
    private static ControladorSimulacion crearControlador(Map<String, String> opciones) {
        ParametrosLCG parametros = new ParametrosLCG(
                entero(opciones, "--a", ConfiguracionSimulacion.A_PRACTICA),
                entero(opciones, "--c", ConfiguracionSimulacion.C_PRACTICA),
                entero(opciones, "--m", ConfiguracionSimulacion.M_PRACTICA),
                entero(opciones, "--semilla", ConfiguracionSimulacion.SEMILLA_PRACTICA));
        ConfiguracionSimulacion configuracion = ConfiguracionSimulacion.paraJava(
                parametros,
                entero(opciones, "--semilla-alternativa", ConfiguracionSimulacion.SEMILLA_ALTERNATIVA),
                enteroInt(opciones, "--n", ConfiguracionSimulacion.CANTIDAD_PRACTICA),
                enteroInt(opciones, "--filas", ConfiguracionSimulacion.FILAS_TABLA),
                opciones.containsKey("--periodo-completo"),
                Path.of(opciones.getOrDefault("--resultados", "resultados")),
                Path.of(opciones.getOrDefault("--comparar-con", "../Python/resultados")));
        return new ControladorSimulacion(
                configuracion,
                GeneradorCongruencialLineal::new,
                new AnalizadorPeriodo(),
                new AnalizadorEstadistico(),
                new ComparadorSecuencias(),
                new RepositorioCSV(),
                new VistaConsola(),
                opciones.containsKey("--sin-graficas") ? null : new VistaGraficosJava2D());
    }

    /** Interpreta los argumentos con la forma "--opcion valor" o "--opcion=valor". */
    private static Map<String, String> leerOpciones(String[] args) {
        Map<String, String> opciones = new HashMap<>();
        for (int i = 0; i < args.length; i++) {
            String clave = args[i];
            String valor = null;
            int igual = clave.indexOf('=');
            if (igual > 0) {
                valor = clave.substring(igual + 1);
                clave = clave.substring(0, igual);
            }
            if (BANDERAS.contains(clave) && valor == null) {
                opciones.put(clave, "");
            } else if (OPCIONES_CON_VALOR.contains(clave)) {
                if (valor == null) {
                    if (i + 1 >= args.length) {
                        throw new IllegalArgumentException("falta el valor de " + clave + ".");
                    }
                    valor = args[++i];
                }
                opciones.put(clave, valor);
            } else {
                throw new IllegalArgumentException("opción no reconocida: " + args[i] + ".");
            }
        }
        return opciones;
    }

    private static long entero(Map<String, String> opciones, String clave, long porDefecto) {
        String texto = opciones.get(clave);
        if (texto == null) {
            return porDefecto;
        }
        try {
            return Long.parseLong(texto.trim());
        } catch (NumberFormatException noEsNumero) {
            throw new IllegalArgumentException("el valor de " + clave + " debe ser un entero (se recibió '" + texto + "').");
        }
    }

    private static int enteroInt(Map<String, String> opciones, String clave, int porDefecto) {
        long valor = entero(opciones, clave, porDefecto);
        if (valor < Integer.MIN_VALUE || valor > Integer.MAX_VALUE) {
            throw new IllegalArgumentException("el valor de " + clave + " es demasiado grande (" + valor + ").");
        }
        return (int) valor;
    }
}
