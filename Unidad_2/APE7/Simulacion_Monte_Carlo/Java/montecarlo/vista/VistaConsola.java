package montecarlo.vista;

import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

import montecarlo.modelo.FilaComparacion;
import montecarlo.modelo.ParametrosLCG;
import montecarlo.modelo.ResultadoEstimacion;
import montecarlo.modelo.ResumenRepeticiones;

/** Presentación de resultados en la terminal. */
public final class VistaConsola {

    private static final int ANCHO = 92;

    public void mostrarEncabezado(ParametrosLCG p, String lenguaje) {
        System.out.println("=".repeat(ANCHO));
        System.out.println(centrar("ESTIMACIÓN DE π MEDIANTE EL MÉTODO DE MONTE CARLO  (" + lenguaje + ")"));
        System.out.println("=".repeat(ANCHO));
        System.out.println("  Modelo:      π ≈ 4 · (Nc / N),  puntos en [-1, 1] x [-1, 1], círculo x² + y² <= 1");
        System.out.println("  Generador:   LCG  X(n+1) = (a · X(n) + c) mod m,  U(n) = X(n) / m");
        imprimir("  Parámetros:  a = %d,  c = %d,  m = %d,  X0 = %d%n", p.a(), p.c(), p.m(), p.semilla());
        imprimir("  Valor real:  π = %.10f%n", Math.PI);
    }

    public void mostrarMuestraLcg(double[] numeros) {
        System.out.println("\n  Primeros números del LCG (verificación con la otra implementación):");
        for (int i = 0; i < numeros.length; i++) {
            imprimir("    U(%2d) = %.10f%n", i + 1, numeros[i]);
        }
    }

    public void mostrarCalentamiento(int nPuntos) {
        imprimir("%n  Calentamiento del JIT: una ejecución sin medir con N = %s puntos.%n", miles(nPuntos));
    }

    public void mostrarResultados(List<ResultadoEstimacion> resultados) {
        titulo("Tabla de resultados (una ejecución por tamaño de muestra)");
        imprimir("  %11s %11s %13s %16s %16s %13s%n",
                "N", "Nc", "π estimado", "Error absoluto", "Error relativo", "Tiempo (ms)");
        for (ResultadoEstimacion r : resultados) {
            imprimir("  %11s %11s %13.6f %16.6f %15.4f%% %13.3f%n", miles(r.nPuntos()), miles(r.puntosDentro()),
                    r.piEstimado(), r.errorAbsoluto(), 100 * r.errorRelativo(), r.tiempoMs());
        }
        resultados.stream().min(Comparator.comparingDouble(ResultadoEstimacion::errorAbsoluto))
                .ifPresent(m -> imprimir("%n  Mejor aproximación: N = %s  (error = %.6f)%n",
                        miles(m.nPuntos()), m.errorAbsoluto()));
    }

    public void mostrarRepeticiones(List<ResumenRepeticiones> resumenes) {
        if (resumenes.isEmpty()) {
            return;
        }
        titulo("Repeticiones con " + resumenes.get(0).repeticiones() + " semillas distintas (variabilidad del error)");
        imprimir("  %11s %13s %12s %13s %12s %12s %10s%n",
                "N", "π promedio", "Desv. est.", "Error medio", "Error mín.", "Error máx.", "1/√N");
        for (ResumenRepeticiones r : resumenes) {
            imprimir("  %11s %13.6f %12.6f %13.6f %12.6f %12.6f %10.6f%n", miles(r.nPuntos()), r.piPromedio(),
                    r.desviacionPi(), r.errorPromedio(), r.errorMinimo(), r.errorMaximo(),
                    1 / Math.sqrt(r.nPuntos()));
        }
    }

    public void mostrarComparacion(List<FilaComparacion> filas) {
        titulo("Comparación Java vs Python");
        if (filas.isEmpty()) {
            System.out.println("  Aún no hay resultados de Python. Ejecute la versión Python y vuelva a ejecutar Java.");
            return;
        }
        imprimir("  %11s %13s %11s %14s %15s %9s %10s%n",
                "N", "π estimado", "Error", "T. Java (ms)", "T. Python (ms)", "Py/Java", "¿Igual π?");
        for (FilaComparacion f : filas) {
            String pi = f.mismaEstimacion()
                    ? formato("%.6f", f.piJava())
                    : formato("%.4f/%.4f", f.piJava(), f.piPython());
            imprimir("  %11s %13s %11.6f %14.3f %15.3f %8.1fx %10s%n", miles(f.nPuntos()), pi, f.errorJava(),
                    f.tiempoJavaMs(), f.tiempoPythonMs(), f.razonTiempos(), f.mismaEstimacion() ? "sí" : "no");
        }
    }

    public void mostrarArchivos(List<Path> rutas) {
        titulo("Archivos generados");
        rutas.forEach(r -> System.out.println("  - " + r));
        System.out.println();
    }

    /** 1000000 -> "1 000 000" (mismo formato que la tabla de la guía). */
    private static String miles(long n) {
        return String.format(Locale.ROOT, "%,d", n).replace(',', ' ');
    }

    private static void titulo(String texto) {
        System.out.println("\n" + "-".repeat(ANCHO));
        System.out.println("  " + texto);
        System.out.println("-".repeat(ANCHO));
    }

    private static String centrar(String texto) {
        int margen = Math.max(0, (ANCHO - texto.length()) / 2);
        return " ".repeat(margen) + texto;
    }

    private static String formato(String plantilla, Object... valores) {
        return String.format(Locale.ROOT, plantilla, valores);
    }

    private static void imprimir(String plantilla, Object... valores) {
        System.out.print(formato(plantilla, valores));
    }
}
