package lcg;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Stream;

import lcg.controlador.ConfiguracionSimulacion;
import lcg.controlador.ControladorSimulacion;
import lcg.modelo.AnalizadorEstadistico;
import lcg.modelo.AnalizadorPeriodo;
import lcg.modelo.ComparadorSecuencias;
import lcg.modelo.GeneradorCongruencialLineal;
import lcg.modelo.Observacion;
import lcg.modelo.ParametrosLCG;
import lcg.modelo.RepositorioCSV;
import lcg.modelo.ResultadoCiclo;
import lcg.modelo.ResultadoComparacion;
import lcg.modelo.ResultadoHullDobell;
import lcg.modelo.ResumenEstadistico;
import lcg.util.FormatoDecimal;
import lcg.vista.VistaConsola;

/**
 * Pruebas de la versión Java (etapa 5 de la simulación: verificación y validación).
 *
 * <p>Usa un ejecutor mínimo propio para no depender de librerías externas: cada
 * prueba es un método que lanza AssertionError si algo no se cumple. Los casos
 * son los mismos que los de las pruebas de Python.
 */
public final class PruebasLCG {

    private static final long M = 1L << 32;
    private static final ParametrosLCG PRACTICA = new ParametrosLCG(1_664_525L, 1_013_904_223L, M, 12_345L);

    private int aprobadas;
    private int fallidas;

    @FunctionalInterface
    private interface Prueba {
        void ejecutar() throws Exception;
    }

    public static void main(String[] args) {
        System.setProperty("java.awt.headless", "true");
        PruebasLCG pruebas = new PruebasLCG();
        pruebas.ejecutar("Primer valor calculado a mano", PruebasLCG::primerValorCalculadoAMano);
        pruebas.ejecutar("Coincide con la secuencia publicada en Numerical Recipes", PruebasLCG::numericalRecipes);
        pruebas.ejecutar("Misma semilla, misma secuencia; reiniciar la reproduce", PruebasLCG::reproducibilidad);
        pruebas.ejecutar("U(n) pertenece a [0, 1) y es X(n)/m", PruebasLCG::valoresNormalizados);
        pruebas.ejecutar("Parámetros fuera de rango se rechazan", PruebasLCG::parametrosInvalidos);
        pruebas.ejecutar("generar(0) y generar(-1)", PruebasLCG::cantidadesLimite);
        pruebas.ejecutar("Hull-Dobell: cada condición por separado", PruebasLCG::hullDobellPorCondicion);
        pruebas.ejecutar("Brent en los escenarios de la práctica", PruebasLCG::brentEscenarios);
        pruebas.ejecutar("Brent = búsqueda directa y período m <=> Hull-Dobell (m = 32)", PruebasLCG::brentExhaustivo);
        pruebas.ejecutar("Mismos a y c: período completo en módulos 2^2 ... 2^18", PruebasLCG::modulosMenores);
        pruebas.ejecutar("Brent respeta el límite de pasos", PruebasLCG::limiteDePasos);
        pruebas.ejecutar("Sin repeticiones en la muestra de 10000 valores", PruebasLCG::sinRepeticiones);
        pruebas.ejecutar("Estadísticos de muestras conocidas", PruebasLCG::estadisticosConocidos);
        pruebas.ejecutar("La secuencia de la práctica se comporta como U(0, 1)", PruebasLCG::estadisticosPractica);
        pruebas.ejecutar("Comparador: idénticas, diferencia y longitudes", PruebasLCG::comparador);
        pruebas.ejecutar("CSV: formato exacto, ida y vuelta y encabezado", PruebasLCG::repositorioCsv);
        pruebas.ejecutar("Formato decimal idéntico al de Python", PruebasLCG::formatoDecimal);
        pruebas.ejecutar("Controlador: 8 pasos y comparación con otra implementación", PruebasLCG::controlador);

        System.out.println();
        System.out.println(pruebas.aprobadas + " pruebas aprobadas, " + pruebas.fallidas + " fallidas.");
        if (pruebas.fallidas > 0) {
            System.exit(1);
        }
    }

    // --------------------------------------------------------------- generador

    private static void primerValorCalculadoAMano() {
        // (1664525 * 12345 + 1013904223) mod 2^32 = 21562465348 mod 4294967296 = 87628868
        Observacion obs = new GeneradorCongruencialLineal(PRACTICA).siguiente();
        iguales(1, obs.n());
        iguales(87_628_868L, obs.x());
        iguales(87_628_868.0 / M, obs.u());
    }

    private static void numericalRecipes() {
        // Numerical Recipes in C (2.a ed., sección 7.1) publica estos valores, en hexadecimal,
        // para el generador a = 1664525, c = 1013904223, m = 2^32 con semilla 0.
        long[] publicados = {0x3C6EF35FL, 0x47502932L, 0xD1CCF6E9L, 0xAAF95334L, 0x6252E503L, 0x9F2EC686L,
                0x57FE6C2DL, 0xA3D95FA8L, 0x81FDBEE7L, 0x94F0AF1AL, 0xCBF633B1L};
        GeneradorCongruencialLineal generador = new GeneradorCongruencialLineal(PRACTICA.conSemilla(0));
        for (long esperado : publicados) {
            iguales(esperado, generador.siguiente().x());
        }
    }

    private static void reproducibilidad() {
        iguales(new GeneradorCongruencialLineal(PRACTICA).generar(1000),
                new GeneradorCongruencialLineal(PRACTICA).generar(1000));
        GeneradorCongruencialLineal generador = new GeneradorCongruencialLineal(PRACTICA);
        List<Observacion> primera = generador.generar(50);
        generador.reiniciar();
        iguales(primera, generador.generar(50));
        generador.transicion(999); // función pura: no debe alterar el estado
        generador.reiniciar();
        iguales(87_628_868L, generador.siguiente().x());
    }

    private static void valoresNormalizados() {
        for (Observacion obs : new GeneradorCongruencialLineal(PRACTICA).generar(10_000)) {
            verificar(obs.u() >= 0 && obs.u() < 1, "U fuera de [0, 1): " + obs);
            iguales((double) obs.x() / M, obs.u());
        }
    }

    private static void parametrosInvalidos() {
        long[][] casos = {
                {5, 3, 1, 0},   // m < 2
                {0, 3, 16, 7},  // a <= 0
                {16, 3, 16, 7}, // a >= m
                {5, -1, 16, 7}, // c < 0
                {5, 16, 16, 7}, // c >= m
                {5, 3, 16, -1}, // semilla < 0
                {5, 3, 16, 16}, // semilla >= m
                {M - 1, 0, M, 1}, // a*(m - 1) + c desborda un long
        };
        for (long[] caso : casos) {
            lanza(IllegalArgumentException.class, () -> new ParametrosLCG(caso[0], caso[1], caso[2], caso[3]));
        }
        ParametrosLCG nuevos = PRACTICA.conSemilla(54_321L);
        iguales(new ParametrosLCG(PRACTICA.a(), PRACTICA.c(), PRACTICA.m(), 54_321L), nuevos);
        iguales(12_345L, PRACTICA.semilla()); // el original es inmutable
    }

    private static void cantidadesLimite() {
        GeneradorCongruencialLineal generador = new GeneradorCongruencialLineal(PRACTICA);
        iguales(List.of(), generador.generar(0));
        lanza(IllegalArgumentException.class, () -> generador.generar(-1));
    }

    // ------------------------------------------------------------------ período

    private static void hullDobellPorCondicion() {
        AnalizadorPeriodo analizador = new AnalizadorPeriodo();
        ResultadoHullDobell practica = analizador.verificarHullDobell(PRACTICA);
        iguales(List.of(2L), practica.factoresPrimosM());
        verificar(practica.periodoCompleto(), "la práctica debe tener período completo");
        // {a, c, m} -> {condición 1, condición 2, condición 3}
        Map<List<Long>, List<Boolean>> casos = Map.of(
                List.of(5L, 3L, 16L), List.of(true, true, true),
                List.of(5L, 2L, 16L), List.of(false, true, true),  // c par
                List.of(3L, 3L, 16L), List.of(true, true, false),  // a - 1 = 2 no es múltiplo de 4
                List.of(4L, 3L, 16L), List.of(true, false, false), // a par
                List.of(6L, 1L, 9L), List.of(true, false, true));  // 9 no es múltiplo de 4
        casos.forEach((p, esperado) -> {
            ResultadoHullDobell r = analizador.verificarHullDobell(new ParametrosLCG(p.get(0), p.get(1), p.get(2), 7));
            iguales(esperado, List.of(r.cCoprimoConM(), r.aMenos1DivisiblePorPrimos(), r.aMenos1MultiploDe4()));
        });
        iguales(List.of(2L, 5L), analizador.verificarHullDobell(new ParametrosLCG(1, 1, 1000, 7)).factoresPrimosM());
        iguales(List.of(97L), analizador.verificarHullDobell(new ParametrosLCG(1, 1, 97, 7)).factoresPrimosM());
    }

    private static void brentEscenarios() {
        // {a, c, m, semilla, lambda, mu}
        long[][] casos = {
                {5, 3, 16, 7, 16, 0},
                {5, 2, 16, 7, 8, 0},
                {3, 3, 16, 7, 8, 0},
                {4, 3, 16, 7, 1, 1},
                {1_664_524, 1_013_904_223, M, 12_345, 1, 16},
        };
        for (long[] caso : casos) {
            ResultadoCiclo r = medir(new ParametrosLCG(caso[0], caso[1], caso[2], caso[3]), AnalizadorPeriodo.SIN_LIMITE);
            iguales(List.of(true, caso[4], caso[5]), List.of(r.encontrado(), r.periodo(), r.inicioCiclo()));
        }
    }

    private static void brentExhaustivo() {
        // Para todo a y c con m = 32: Brent y la búsqueda con diccionario dan el mismo ciclo,
        // y el período es m si y solo si se cumplen las condiciones de Hull-Dobell.
        AnalizadorPeriodo analizador = new AnalizadorPeriodo();
        int m = 32;
        for (int a = 1; a < m; a++) {
            for (int c = 0; c < m; c++) {
                ParametrosLCG p = new ParametrosLCG(a, c, m, 7);
                ResultadoCiclo brent = medir(p, AnalizadorPeriodo.SIN_LIMITE);
                ResultadoCiclo directo = analizador.buscarRepeticion(7, new GeneradorCongruencialLineal(p).generar(m + 1));
                iguales(List.of(directo.periodo(), directo.inicioCiclo()), List.of(brent.periodo(), brent.inicioCiclo()));
                iguales(analizador.verificarHullDobell(p).periodoCompleto(), brent.periodo() == m);
            }
        }
    }

    private static void modulosMenores() {
        // Reducir a y c módulo 2^k conserva las condiciones de Hull-Dobell: el período debe ser 2^k.
        for (int k = 2; k <= 18; k++) {
            long m = 1L << k;
            ResultadoCiclo r = medir(new ParametrosLCG(PRACTICA.a() % m, PRACTICA.c() % m, m, PRACTICA.semilla() % m),
                    AnalizadorPeriodo.SIN_LIMITE);
            iguales(List.of(m, 0L), List.of(r.periodo(), r.inicioCiclo()));
        }
    }

    private static void limiteDePasos() {
        ResultadoCiclo r = medir(PRACTICA, 1000);
        verificar(!r.encontrado(), "no debería cerrar el ciclo en 1000 pasos");
        iguales(1000L, r.pasos());
    }

    private static void sinRepeticiones() {
        ResultadoCiclo r = new AnalizadorPeriodo().buscarRepeticion(
                PRACTICA.semilla(), new GeneradorCongruencialLineal(PRACTICA).generar(10_000));
        verificar(!r.encontrado(), "no debe haber repeticiones");
        iguales(10_000L, r.pasos());
    }

    // ------------------------------------------------------------- estadística

    private static void estadisticosConocidos() {
        AnalizadorEstadistico analizador = new AnalizadorEstadistico();
        List<Double> uniforme = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            uniforme.add((i + 0.5) / 10);
        }
        ResumenEstadistico r = analizador.analizar(muestra(uniforme));
        iguales(List.of(1, 1, 1, 1, 1, 1, 1, 1, 1, 1), r.frecuencias());
        cercanos(0.5, r.media(), 1e-12);
        iguales(0.0, r.chiCuadrado());

        List<Double> concentrada = new ArrayList<>(java.util.Collections.nCopies(99, 0.05));
        concentrada.add(0.95);
        r = analizador.analizar(muestra(concentrada));
        iguales(99, r.frecuencias().get(0));
        verificar(!r.pasaChiCuadrado(), "una muestra concentrada debe rechazar la uniformidad");

        List<Double> alternante = new ArrayList<>();
        for (int i = 0; i < 50; i++) {
            alternante.add(0.25);
            alternante.add(0.75);
        }
        cercanos(-0.99, analizador.analizar(muestra(alternante)).autocorrelacionLag1(), 1e-12);
        lanza(IllegalArgumentException.class, () -> analizador.analizar(muestra(List.of(0.5))));
    }

    private static void estadisticosPractica() {
        ResumenEstadistico r = new AnalizadorEstadistico().analizar(new GeneradorCongruencialLineal(PRACTICA).generar(10_000));
        iguales(10_000, r.frecuencias().stream().mapToInt(Integer::intValue).sum());
        cercanos(0.5, r.media(), 0.01);
        cercanos(1.0 / 12, r.varianza(), 0.005);
        verificar(r.pasaChiCuadrado(), "debe aceptarse la uniformidad");
        verificar(Math.abs(r.autocorrelacionLag1()) < 1.96 / Math.sqrt(10_000), "autocorrelación fuera de la banda del 95 %");
        // Mismos valores que imprime la versión Python (bucles en el mismo orden, double IEEE 754).
        iguales("14.1600", FormatoDecimal.formatear(r.chiCuadrado(), 4));
        iguales("-0.015311", FormatoDecimal.formatear(r.autocorrelacionLag1(), 6));
    }

    // ------------------------------------------------------ comparación y CSV

    private static void comparador() {
        ComparadorSecuencias comparador = new ComparadorSecuencias();
        List<Observacion> a = generar(PRACTICA, 100);
        ResultadoComparacion r = comparador.comparar(a, generar(PRACTICA, 100));
        verificar(r.identicas(), "deben ser idénticas");
        iguales(100, r.coincidencias());
        verificar(r.primeraDiscrepancia().isEmpty(), "no debe haber discrepancias");

        List<Observacion> b = new ArrayList<>(a);
        Observacion quinta = b.get(4);
        b.set(4, new Observacion(quinta.n(), quinta.x() + 1, quinta.u()));
        r = comparador.comparar(a, b);
        verificar(!r.identicas(), "no deben ser idénticas");
        iguales(5, r.primeraDiscrepancia().getAsInt());

        r = comparador.comparar(a, a.subList(0, 80));
        iguales(List.of(80, 80), List.of(r.comparadas(), r.coincidencias()));
        verificar(!r.identicas(), "longitudes distintas no son idénticas");

        iguales(0, comparador.comparar(generar(PRACTICA, 1000), generar(PRACTICA.conSemilla(54_321L), 1000)).coincidencias());
    }

    private static void repositorioCsv() throws IOException {
        Path carpeta = Files.createTempDirectory("lcg-csv");
        try {
            RepositorioCSV repositorio = new RepositorioCSV();
            Path ruta = carpeta.resolve("secuencia.csv");
            repositorio.guardar(generar(PRACTICA, 2), ruta);
            iguales("n,X_n,U_n\n1,87628868,0.0204026857\n2,71072467,0.0165478482\n", Files.readString(ruta));

            // U = 2^21 / 2^32 = 0.00048828125: empate exacto en el 11.o decimal, se redondea al par.
            repositorio.guardar(List.of(new Observacion(1, 1L << 21, (double) (1L << 21) / M)), ruta);
            iguales("1,2097152,0.0004882812", Files.readAllLines(ruta).get(1));

            List<Observacion> originales = generar(PRACTICA, 500);
            repositorio.guardar(originales, ruta);
            List<Observacion> cargadas = repositorio.cargar(ruta);
            iguales(originales.size(), cargadas.size());
            for (int i = 0; i < originales.size(); i++) {
                iguales(originales.get(i).x(), cargadas.get(i).x());
                cercanos(originales.get(i).u(), cargadas.get(i).u(), 5e-11);
            }

            Files.writeString(ruta, "a,b,c\n1,2,3\n");
            lanza(IOException.class, () -> repositorio.cargar(ruta));
        } finally {
            borrar(carpeta);
        }
    }

    private static void formatoDecimal() {
        // Resultados obtenidos con Python: f"{valor:.{decimales}f}".
        iguales("0.12", FormatoDecimal.formatear(0.125, 2));
        iguales("0.38", FormatoDecimal.formatear(0.375, 2));
        iguales("-0.000000", FormatoDecimal.formatear(-1e-7, 6));
        iguales("2", FormatoDecimal.formatear(2.5, 0));
        iguales("4", FormatoDecimal.formatear(3.5, 0));
        iguales("-0.00", FormatoDecimal.formatear(-0.0, 2));
        iguales("nan", FormatoDecimal.formatear(Double.NaN, 3));
    }

    // -------------------------------------------------------------- integración

    private static void controlador() throws IOException {
        Path carpeta = Files.createTempDirectory("lcg-controlador");
        try {
            String sinComparar = ejecutarControlador(carpeta, null);
            for (String paso : List.of("Paso 1.", "Pasos 2 y 3.", "Paso 4.", "Paso 5.", "Paso 6.", "Paso 7.", "Paso 8.")) {
                verificar(sinComparar.contains(paso), "falta " + paso);
            }
            for (long semilla : List.of(12_345L, 54_321L)) {
                verificar(Files.isRegularFile(carpeta.resolve("java").resolve("secuencia_java_semilla_" + semilla + ".csv")),
                        "falta el CSV de la semilla " + semilla);
            }

            // Simula la carpeta de resultados de Python con archivos del mismo algoritmo.
            Path carpetaPython = carpeta.resolve("python");
            for (long semilla : List.of(12_345L, 54_321L)) {
                new RepositorioCSV().guardar(generar(PRACTICA.conSemilla(semilla), 500),
                        carpetaPython.resolve("secuencia_python_semilla_" + semilla + ".csv"));
            }
            String comparando = ejecutarControlador(carpeta, carpetaPython);
            iguales(2, comparando.split("Veredicto: las secuencias son IDÉNTICAS.", -1).length - 1);
            verificar(Files.isRegularFile(carpeta.resolve("java").resolve("comparacion_java_python_semilla_12345.csv")),
                    "falta la tabla de comparación");
        } finally {
            borrar(carpeta);
        }
    }

    private static String ejecutarControlador(Path carpeta, Path carpetaExterna) throws IOException {
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        ConfiguracionSimulacion configuracion = ConfiguracionSimulacion.paraJava(
                PRACTICA, 54_321L, 500, 20, false, carpeta.resolve("java"), carpetaExterna);
        new ControladorSimulacion(configuracion, GeneradorCongruencialLineal::new, new AnalizadorPeriodo(),
                new AnalizadorEstadistico(), new ComparadorSecuencias(), new RepositorioCSV(),
                new VistaConsola(new PrintStream(buffer, true, StandardCharsets.UTF_8)), null).ejecutar();
        return buffer.toString(StandardCharsets.UTF_8);
    }

    // --------------------------------------------------------------- utilidades

    private void ejecutar(String nombre, Prueba prueba) {
        try {
            prueba.ejecutar();
            aprobadas++;
            System.out.println("  [OK]    " + nombre);
        } catch (Throwable error) { // AssertionError o cualquier excepción inesperada
            fallidas++;
            System.out.println("  [FALLA] " + nombre + ": " + error);
        }
    }

    private static ResultadoCiclo medir(ParametrosLCG parametros, long limite) {
        GeneradorCongruencialLineal generador = new GeneradorCongruencialLineal(parametros);
        return new AnalizadorPeriodo().medirPeriodo(generador::transicion, parametros.semilla(), limite);
    }

    private static List<Observacion> generar(ParametrosLCG parametros, int cantidad) {
        return new GeneradorCongruencialLineal(parametros).generar(cantidad);
    }

    /** Observaciones a partir de valores U (X no interviene en la estadística). */
    private static List<Observacion> muestra(List<Double> valores) {
        List<Observacion> observaciones = new ArrayList<>();
        for (int i = 0; i < valores.size(); i++) {
            observaciones.add(new Observacion(i + 1, 0, valores.get(i)));
        }
        return observaciones;
    }

    private static void verificar(boolean condicion, String mensaje) {
        if (!condicion) {
            throw new AssertionError(mensaje);
        }
    }

    private static void iguales(Object esperado, Object obtenido) {
        verificar(Objects.equals(esperado, obtenido), "se esperaba " + esperado + " y se obtuvo " + obtenido);
    }

    private static void cercanos(double esperado, double obtenido, double tolerancia) {
        verificar(Math.abs(esperado - obtenido) <= tolerancia, "se esperaba " + esperado + " y se obtuvo " + obtenido);
    }

    private static void lanza(Class<? extends Throwable> tipo, Prueba accion) {
        try {
            accion.ejecutar();
        } catch (Throwable error) {
            verificar(tipo.isInstance(error), "se esperaba " + tipo.getSimpleName() + " y se lanzó " + error);
            return;
        }
        throw new AssertionError("se esperaba " + tipo.getSimpleName() + " y no se lanzó nada");
    }

    private static void borrar(Path carpeta) throws IOException {
        try (Stream<Path> rutas = Files.walk(carpeta)) {
            for (Path ruta : rutas.sorted(Comparator.reverseOrder()).toList()) {
                Files.delete(ruta);
            }
        }
    }
}
