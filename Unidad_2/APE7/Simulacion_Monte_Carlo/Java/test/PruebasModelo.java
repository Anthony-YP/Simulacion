import java.util.function.BooleanSupplier;

import montecarlo.modelo.EstimadorPiMonteCarlo;
import montecarlo.modelo.ExperimentoMonteCarlo;
import montecarlo.modelo.GeneradorCongruencialLineal;
import montecarlo.modelo.ParametrosLCG;
import montecarlo.modelo.ResumenRepeticiones;

/** Verificación del modelo sin dependencias externas: java -cp out PruebasModelo */
public final class PruebasModelo {

    private static int aprobadas;
    private static int fallidas;

    private PruebasModelo() {
    }

    public static void main(String[] args) {
        ParametrosLCG nr = ParametrosLCG.NUMERICAL_RECIPES;
        EstimadorPiMonteCarlo estimador = new EstimadorPiMonteCarlo();

        probar("Secuencia calculada a mano (a=5, c=3, m=16, X0=7 -> 6, 1, 8)", () -> {
            GeneradorCongruencialLineal g = new GeneradorCongruencialLineal(new ParametrosLCG(5, 3, 16, 7));
            return g.siguienteEntero() == 6 && g.siguienteEntero() == 1 && g.siguienteEntero() == 8;
        });
        probar("Primer valor de Numerical Recipes", () ->
                new GeneradorCongruencialLineal(nr).siguienteEntero() == (1_664_525L * 12_345 + 1_013_904_223L) % (1L << 32));
        probar("Valores en [0, 1)", () -> {
            for (double u : new GeneradorCongruencialLineal(nr).generar(10_000)) {
                if (u < 0.0 || u >= 1.0) {
                    return false;
                }
            }
            return true;
        });
        probar("Reiniciar reproduce la secuencia", () -> {
            GeneradorCongruencialLineal g = new GeneradorCongruencialLineal(nr);
            double[] primera = g.generar(100);
            g.reiniciar();
            return java.util.Arrays.equals(primera, g.generar(100));
        });
        probar("Parámetros inválidos lanzan excepción", () -> {
            try {
                new ParametrosLCG(5, 0, 16, 0);
                return false;
            } catch (IllegalArgumentException e) {
                return true;
            }
        });
        probar("Conteo de puntos conocidos: (0,0) y (0,-1) dentro; (0.98,0.98) fuera", () -> {
            double[] valores = {0.5, 0.5, 0.99, 0.99, 0.5, 0.0};
            int[] i = {0};
            return estimador.contarDentro(() -> valores[i[0]++], 3) == 2;
        });
        probar("Fórmula π = 4·Nc/N", () -> Math.abs(estimador.calcularPi(785, 1000) - 3.14) < 1e-12);
        probar("El muestreo para graficar coincide con el conteo", () ->
                estimador.muestrearPuntos(new GeneradorCongruencialLineal(nr), 5_000).cantidadDentro()
                        == estimador.contarDentro(new GeneradorCongruencialLineal(nr), 5_000));

        ExperimentoMonteCarlo experimento = new ExperimentoMonteCarlo(nr, estimador);
        double p = Math.PI / 4;
        probar("Validación: estimación con N = 100 000 dentro de 4 errores estándar", () ->
                experimento.ejecutar(100_000).errorAbsoluto() < 4 * 4 * Math.sqrt(p * (1 - p) / 100_000));
        probar("Validación: la dispersión de π̂ coincide con la teoría (N = 1 000)", () -> {
            ResumenRepeticiones r = experimento.repetir(1_000, experimento.semillasRepeticiones(30));
            double teorica = 4 * Math.sqrt(p * (1 - p) / 1_000);
            return r.desviacionPi() > 0.5 * teorica && r.desviacionPi() < 2 * teorica;
        });
        probar("Validación: el error medio disminuye al aumentar N", () -> {
            long[] semillas = experimento.semillasRepeticiones(10);
            return experimento.repetir(100_000, semillas).errorPromedio()
                    < experimento.repetir(1_000, semillas).errorPromedio();
        });

        System.out.printf("%nPruebas aprobadas: %d, fallidas: %d%n", aprobadas, fallidas);
        if (fallidas > 0) {
            System.exit(1);
        }
    }

    private static void probar(String nombre, BooleanSupplier prueba) {
        boolean ok;
        try {
            ok = prueba.getAsBoolean();
        } catch (RuntimeException e) {
            ok = false;
        }
        System.out.println((ok ? "  [OK]    " : "  [FALLA] ") + nombre);
        if (ok) {
            aprobadas++;
        } else {
            fallidas++;
        }
    }
}
