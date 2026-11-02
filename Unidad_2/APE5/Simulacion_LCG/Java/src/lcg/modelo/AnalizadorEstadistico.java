package lcg.modelo;

import java.util.ArrayList;
import java.util.List;

/**
 * Calcula media, varianza, frecuencias, chi-cuadrado y autocorrelación de U(n).
 *
 * <p>Las sumas se hacen con bucles simples en el mismo orden que la versión
 * Python; como ambos lenguajes usan double IEEE 754, los resultados son
 * idénticos hasta el último decimal.
 */
public final class AnalizadorEstadistico {

    public static final int INTERVALOS = 10;
    /** Valor crítico de tablas chi-cuadrado: alfa = 0.05 y 10 - 1 = 9 grados de libertad. */
    public static final double VALOR_CRITICO_CHI_CUADRADO = 16.919;

    public ResumenEstadistico analizar(List<Observacion> observaciones) {
        int n = observaciones.size();
        if (n < 2) {
            throw new IllegalArgumentException("Se necesitan al menos 2 observaciones para el análisis.");
        }
        double[] valores = new double[n];
        for (int i = 0; i < n; i++) {
            valores[i] = observaciones.get(i).u();
        }

        double total = 0.0;
        for (double u : valores) {
            total += u;
        }
        double media = total / n;

        // Suma de cuadrados de las desviaciones: numerador de la varianza muestral
        // y denominador de la autocorrelación.
        double sumaCuadrados = 0.0;
        for (double u : valores) {
            double desviacion = u - media;
            sumaCuadrados += desviacion * desviacion;
        }

        // Autocorrelación de retardo 1: relación entre cada U(n) y su sucesor U(n+1).
        double sumaProductos = 0.0;
        for (int i = 0; i < n - 1; i++) {
            sumaProductos += (valores[i] - media) * (valores[i + 1] - media);
        }

        int[] frecuencias = frecuencias(valores);
        double esperada = (double) n / INTERVALOS; // frecuencia esperada si la muestra es uniforme
        double chiCuadrado = 0.0;
        for (int observada : frecuencias) {
            double diferencia = observada - esperada;
            chiCuadrado += diferencia * diferencia / esperada;
        }

        double minimo = valores[0];
        double maximo = valores[0];
        for (double u : valores) {
            minimo = Math.min(minimo, u);
            maximo = Math.max(maximo, u);
        }

        List<Integer> listaFrecuencias = new ArrayList<>(INTERVALOS);
        for (int frecuencia : frecuencias) {
            listaFrecuencias.add(frecuencia);
        }
        // Si todos los valores son iguales no hay variación y la autocorrelación no está definida.
        double autocorrelacion = sumaCuadrados > 0 ? sumaProductos / sumaCuadrados : Double.NaN;
        return new ResumenEstadistico(n, media, sumaCuadrados / (n - 1), minimo, maximo, listaFrecuencias,
                chiCuadrado, VALOR_CRITICO_CHI_CUADRADO, autocorrelacion);
    }

    /** Cuenta cuántos valores caen en cada intervalo [i/k, (i+1)/k). */
    private static int[] frecuencias(double[] valores) {
        int[] conteo = new int[INTERVALOS];
        for (double u : valores) {
            // Math.min protege el caso límite en que u * k redondee a k.
            conteo[Math.min((int) (u * INTERVALOS), INTERVALOS - 1)]++;
        }
        return conteo;
    }
}
