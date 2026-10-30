package lcg.vista;

import java.io.PrintStream;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.OptionalInt;
import java.util.Set;

import lcg.modelo.AnalisisEscenario;
import lcg.modelo.AnalisisSecuencia;
import lcg.modelo.FilaComparacion;
import lcg.modelo.Observacion;
import lcg.modelo.ParametrosLCG;
import lcg.modelo.ResultadoCiclo;
import lcg.modelo.ResultadoComparacion;
import lcg.modelo.ResultadoHullDobell;
import lcg.modelo.ResumenEstadistico;
import lcg.util.FormatoDecimal;

/**
 * Imprime los resultados en la salida estándar (o en el flujo que se le indique).
 *
 * <p>Produce exactamente el mismo texto que la VistaConsola de Python (mismos
 * títulos, tablas y número de decimales), de modo que las dos salidas se pueden
 * comparar línea por línea.
 */
public final class VistaConsola implements VistaResultados {

    private static final int ANCHO = 78;
    private static final String SANGRIA = "  ";
    private static final int DECIMALES_U = 10;

    private final PrintStream salida;

    public VistaConsola() {
        this(System.out);
    }

    /** Recibir el flujo permite redirigir la salida, por ejemplo, a un archivo. */
    public VistaConsola(PrintStream salida) {
        this.salida = Objects.requireNonNull(salida, "salida");
    }

    // ------------------------------------------------------------------ contrato

    @Override
    public void mostrarTitulo(String implementacion) {
        imprimir("=".repeat(ANCHO));
        imprimir(SANGRIA + "GENERADOR CONGRUENCIAL LINEAL (LCG) - Implementación en " + implementacion);
        imprimir(SANGRIA + "X(n+1) = (a * X(n) + c) mod m          U(n) = X(n) / m");
        imprimir("=".repeat(ANCHO));
    }

    @Override
    public void mostrarSeccion(String titulo) {
        imprimir("");
        imprimir("-".repeat(ANCHO));
        imprimir(SANGRIA + titulo);
        imprimir("-".repeat(ANCHO));
    }

    @Override
    public void mostrarMensaje(String texto) {
        imprimir(SANGRIA + texto);
    }

    @Override
    public void mostrarParametros(ParametrosLCG parametros, int cantidad) {
        tabla(List.of("Parámetro", "Descripción", "Valor"),
                List.of(
                        List.of("a", "Multiplicador", String.valueOf(parametros.a())),
                        List.of("c", "Incremento", String.valueOf(parametros.c())),
                        List.of("m", "Módulo", modulo(parametros.m())),
                        List.of("X(0)", "Semilla", String.valueOf(parametros.semilla())),
                        List.of("N", "Valores a generar", String.valueOf(cantidad))),
                Set.of(0, 1));
    }

    @Override
    public void mostrarObservaciones(List<Observacion> observaciones) {
        List<List<String>> filas = new ArrayList<>();
        for (Observacion obs : observaciones) {
            filas.add(List.of(String.valueOf(obs.n()), String.valueOf(obs.x()), decimal(obs.u(), DECIMALES_U)));
        }
        tabla(List.of("n", "X(n)", "U(n)"), filas, Set.of());
    }

    @Override
    public void mostrarComparacion(ResultadoComparacion resultado, String etiquetaA, String etiquetaB, int filas) {
        if (filas > 0) {
            List<List<String>> contenido = new ArrayList<>();
            for (FilaComparacion f : resultado.filas().subList(0, Math.min(filas, resultado.comparadas()))) {
                contenido.add(List.of(String.valueOf(f.n()), String.valueOf(f.xA()), String.valueOf(f.xB()),
                        decimal(f.uA(), DECIMALES_U), decimal(f.uB(), DECIMALES_U), f.coincide() ? "Sí" : "No"));
            }
            tabla(List.of("n", "X(n) " + etiquetaA, "X(n) " + etiquetaB,
                    "U(n) " + etiquetaA, "U(n) " + etiquetaB, "¿Coincide?"), contenido, Set.of(5));
        }
        mostrarMensaje(etiquetaA + " vs " + etiquetaB + ": " + resultado.coincidencias() + " de "
                + resultado.comparadas() + " posiciones coinciden (longitudes " + resultado.longitudA()
                + " y " + resultado.longitudB() + ").");
        mostrarMensaje("Diferencia máxima en U(n): " + decimal(resultado.diferenciaMaximaU(), DECIMALES_U));
        OptionalInt primera = resultado.primeraDiscrepancia();
        if (resultado.identicas()) {
            mostrarMensaje("Veredicto: las secuencias son IDÉNTICAS.");
        } else if (primera.isEmpty()) {
            mostrarMensaje("Veredicto: las secuencias son DISTINTAS (tienen longitudes diferentes).");
        } else {
            mostrarMensaje("Veredicto: las secuencias son DISTINTAS (primera diferencia en n = "
                    + primera.getAsInt() + ").");
        }
    }

    @Override
    public void mostrarPeriodo(AnalisisSecuencia analisis, ResultadoCiclo ciclo, double segundos) {
        ParametrosLCG p = analisis.parametros();
        ResultadoHullDobell hd = analisis.hullDobell();
        long aMenos1 = p.a() - 1;
        List<String> divisiones = new ArrayList<>();
        for (long primo : hd.factoresPrimosM()) {
            divisiones.add(aMenos1 + " mod " + primo + " = " + (aMenos1 % primo));
        }
        mostrarMensaje("Teorema de Hull-Dobell: el período es completo (igual a m) si y solo si");
        mostrarMensaje("se cumplen las tres condiciones siguientes.");
        tabla(List.of("#", "Condición", "Verificación", "Resultado"),
                List.of(
                        List.of("1", "mcd(c, m) = 1", "mcd(" + p.c() + ", " + p.m() + ") = " + hd.mcdCM(),
                                cumple(hd.cCoprimoConM())),
                        List.of("2", "a - 1 divisible por cada primo de m", String.join(", ", divisiones),
                                cumple(hd.aMenos1DivisiblePorPrimos())),
                        List.of("3", "Si 4 divide a m, 4 divide a a - 1",
                                "m mod 4 = " + (p.m() % 4) + "; (a - 1) mod 4 = " + (aMenos1 % 4),
                                cumple(hd.aMenos1MultiploDe4()))),
                Set.of(1, 2, 3));
        if (hd.periodoCompleto()) {
            mostrarMensaje("Período teórico: " + p.m() + " (completo: recorre los m valores antes de repetirse).");
        } else {
            mostrarMensaje("Período teórico: menor que m = " + p.m() + " (no hay período completo).");
        }

        ResultadoCiclo repeticion = analisis.repeticion();
        int cantidad = analisis.estadisticas().cantidad();
        if (repeticion.encontrado()) {
            mostrarMensaje("Muestra de " + cantidad + " valores: X(" + (repeticion.inicioCiclo() + repeticion.periodo())
                    + ") repite a X(" + repeticion.inicioCiclo() + "); período observado = "
                    + repeticion.periodo() + ".");
        } else {
            String porcentaje = decimal(100.0 * cantidad / p.m(), 6);
            mostrarMensaje("Muestra de " + cantidad + " valores: ningún valor se repite, el ciclo es mayor que "
                    + cantidad + ".");
            mostrarMensaje("La muestra usa " + cantidad + " de " + p.m() + " valores del ciclo (" + porcentaje + " %).");
        }

        if (ciclo == null) {
            mostrarMensaje("Medición exhaustiva (Brent): no ejecutada; use --periodo-completo.");
        } else if (ciclo.encontrado()) {
            mostrarMensaje("Medición exhaustiva (Brent): período = " + ciclo.periodo() + ", inicio del ciclo = "
                    + ciclo.inicioCiclo() + ".");
            mostrarMensaje("Evaluaciones de f: " + ciclo.pasos() + "; tiempo: " + decimal(segundos, 2) + " s.");
        } else {
            mostrarMensaje("Medición exhaustiva (Brent): el ciclo no se cerró en " + ciclo.pasos() + " evaluaciones.");
        }
    }

    @Override
    public void mostrarEscenarios(List<AnalisisEscenario> analisis, int filas) {
        mostrarMensaje("Escenarios: período con parámetros adecuados e inadecuados.");
        mostrarMensaje("mu = posición donde empieza el ciclo; lambda = longitud del ciclo (período).");
        List<List<String>> resumen = new ArrayList<>();
        for (int i = 0; i < analisis.size(); i++) {
            AnalisisEscenario item = analisis.get(i);
            ParametrosLCG p = item.escenario().parametros();
            ResultadoCiclo ciclo = item.ciclo();
            resumen.add(List.of("E" + (i + 1), item.escenario().nombre(), String.valueOf(p.a()),
                    String.valueOf(p.c()), String.valueOf(p.m()), String.valueOf(p.semilla()),
                    cumple(item.hullDobell().periodoCompleto()),
                    ciclo.encontrado() ? String.valueOf(ciclo.inicioCiclo()) : "-",
                    ciclo.encontrado() ? String.valueOf(ciclo.periodo()) : "-"));
        }
        tabla(List.of("Id", "Escenario", "a", "c", "m", "X(0)", "Hull-Dobell", "mu", "lambda"), resumen,
                Set.of(1, 6));

        mostrarMensaje("Primeros valores X(n) de cada escenario (n = 0 es la semilla):");
        int cantidad = filas;
        List<String> encabezados = new ArrayList<>(List.of("n"));
        for (int i = 0; i < analisis.size(); i++) {
            encabezados.add("E" + (i + 1));
            cantidad = Math.min(cantidad, analisis.get(i).valores().size());
        }
        List<List<String>> valores = new ArrayList<>();
        for (int n = 0; n < cantidad; n++) {
            List<String> fila = new ArrayList<>(List.of(String.valueOf(n)));
            for (AnalisisEscenario item : analisis) {
                fila.add(String.valueOf(item.valores().get(n)));
            }
            valores.add(fila);
        }
        tabla(encabezados, valores, Set.of());
    }

    @Override
    public void mostrarComparacionSemillas(AnalisisSecuencia a, AnalisisSecuencia b) {
        ResumenEstadistico ea = a.estadisticas();
        ResumenEstadistico eb = b.estadisticas();
        tabla(List.of("Estadístico", "Semilla " + a.parametros().semilla(), "Semilla " + b.parametros().semilla(),
                        "Ideal U(0,1)"),
                List.of(
                        List.of("Valores analizados", String.valueOf(ea.cantidad()), String.valueOf(eb.cantidad()), "-"),
                        List.of("Media", decimal(ea.media(), 6), decimal(eb.media(), 6), decimal(0.5, 6)),
                        List.of("Varianza", decimal(ea.varianza(), 6), decimal(eb.varianza(), 6),
                                decimal(1.0 / 12, 6)),
                        List.of("Desviación estándar", decimal(ea.desviacionEstandar(), 6),
                                decimal(eb.desviacionEstandar(), 6), decimal(Math.sqrt(1.0 / 12), 6)),
                        List.of("Mínimo", decimal(ea.minimo(), 6), decimal(eb.minimo(), 6), decimal(0.0, 6)),
                        List.of("Máximo", decimal(ea.maximo(), 6), decimal(eb.maximo(), 6), decimal(1.0, 6)),
                        List.of("Chi-cuadrado (10 intervalos)", decimal(ea.chiCuadrado(), 4),
                                decimal(eb.chiCuadrado(), 4), "< " + decimal(ea.valorCriticoChiCuadrado(), 3)),
                        List.of("Uniformidad (alfa = 0.05)", uniformidad(ea), uniformidad(eb), "Se acepta"),
                        List.of("Autocorrelación lag 1", decimal(ea.autocorrelacionLag1(), 6),
                                decimal(eb.autocorrelacionLag1(), 6), decimal(0.0, 6)),
                        List.of("Período teórico", periodoTeorico(a), periodoTeorico(b), "-"),
                        List.of("Valores repetidos en la muestra", repetidos(a.repeticion()),
                                repetidos(b.repeticion()), "Ninguno")),
                Set.of(0));
    }

    @Override
    public void mostrarSinComparacion(String implementacion, Path ruta) {
        mostrarMensaje("No se encontraron resultados de " + implementacion + ": " + rutaLegible(ruta));
        mostrarMensaje("Ejecute la versión " + implementacion + " y vuelva a ejecutar este programa para comparar.");
    }

    @Override
    public void mostrarArchivos(List<Path> rutas) {
        imprimir("");
        imprimir("=".repeat(ANCHO));
        mostrarMensaje("Archivos generados:");
        for (Path ruta : rutas) {
            mostrarMensaje("  - " + rutaLegible(ruta));
        }
        imprimir("=".repeat(ANCHO));
    }

    // ------------------------------------------------------------- utilidades

    private void imprimir(String texto) {
        salida.println(texto);
    }

    /**
     * Dibuja una tabla con bordes ASCII; cada columna toma el ancho de su celda más larga.
     * Las columnas de {@code izquierda} se alinean a la izquierda (texto) y el resto a la
     * derecha (números), para que las cifras queden encolumnadas.
     */
    private void tabla(List<String> encabezados, List<List<String>> filas, Set<Integer> izquierda) {
        int[] anchos = new int[encabezados.size()];
        for (int i = 0; i < anchos.length; i++) {
            anchos[i] = encabezados.get(i).length();
        }
        for (List<String> fila : filas) {
            for (int i = 0; i < anchos.length; i++) {
                anchos[i] = Math.max(anchos[i], fila.get(i).length());
            }
        }
        StringBuilder borde = new StringBuilder("+");
        for (int ancho : anchos) {
            borde.append("-".repeat(ancho + 2)).append('+');
        }
        StringBuilder cabecera = new StringBuilder("|");
        for (int i = 0; i < anchos.length; i++) {
            cabecera.append(' ').append(centrar(encabezados.get(i), anchos[i])).append(" |");
        }
        imprimir(SANGRIA + borde);
        imprimir(SANGRIA + cabecera);
        imprimir(SANGRIA + borde);
        for (List<String> fila : filas) {
            StringBuilder linea = new StringBuilder("|");
            for (int i = 0; i < anchos.length; i++) {
                String celda = fila.get(i);
                String relleno = " ".repeat(anchos[i] - celda.length());
                linea.append(' ').append(izquierda.contains(i) ? celda + relleno : relleno + celda).append(" |");
            }
            imprimir(SANGRIA + linea);
        }
        imprimir(SANGRIA + borde);
    }

    /** El espacio sobrante va a la derecha, la misma regla que usa la versión Python. */
    private static String centrar(String texto, int ancho) {
        int izquierda = (ancho - texto.length()) / 2;
        return " ".repeat(izquierda) + texto + " ".repeat(ancho - texto.length() - izquierda);
    }

    private static String decimal(double valor, int decimales) {
        return FormatoDecimal.formatear(valor, decimales);
    }

    /** Muestra m y, si es potencia de 2, también su exponente (por ejemplo 2^32). */
    private static String modulo(long m) {
        boolean esPotenciaDe2 = (m & (m - 1)) == 0;
        return esPotenciaDe2 ? m + " (2^" + Long.numberOfTrailingZeros(m) + ")" : String.valueOf(m);
    }

    private static String cumple(boolean condicion) {
        return condicion ? "Cumple" : "No cumple";
    }

    private static String uniformidad(ResumenEstadistico resumen) {
        return resumen.pasaChiCuadrado() ? "Se acepta" : "Se rechaza";
    }

    private static String periodoTeorico(AnalisisSecuencia analisis) {
        long m = analisis.parametros().m();
        return analisis.hullDobell().periodoCompleto() ? String.valueOf(m) : "< " + m;
    }

    private static String repetidos(ResultadoCiclo repeticion) {
        return repeticion.encontrado() ? "Sí (período " + repeticion.periodo() + ")" : "Ninguno";
    }

    /** Ruta relativa al directorio actual, con '/' como separador. */
    private static String rutaLegible(Path ruta) {
        try {
            Path actual = Path.of("").toAbsolutePath();
            return actual.relativize(ruta.toAbsolutePath().normalize()).toString().replace('\\', '/');
        } catch (IllegalArgumentException distintaUnidad) { // en Windows, rutas en unidades distintas
            return ruta.toString();
        }
    }
}
