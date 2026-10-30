package lcg.modelo;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.LongUnaryOperator;

/** Determina el período de un generador de forma teórica y empírica. */
public final class AnalizadorPeriodo {

    /** Límite usado cuando se quiere recorrer el ciclo completo. */
    public static final long SIN_LIMITE = Long.MAX_VALUE;

    /** Evalúa las tres condiciones del teorema de Hull-Dobell con los parámetros dados. */
    public ResultadoHullDobell verificarHullDobell(ParametrosLCG parametros) {
        long a = parametros.a();
        long c = parametros.c();
        long m = parametros.m();
        List<Long> primos = factoresPrimos(m);
        long mcd = mcd(c, m);
        boolean divisiblePorPrimos = primos.stream().allMatch(primo -> (a - 1) % primo == 0);
        // Si m no es múltiplo de 4, la condición 3 no aplica y se da por cumplida.
        boolean multiploDe4 = m % 4 != 0 || (a - 1) % 4 == 0;
        return new ResultadoHullDobell(primos, mcd, mcd == 1, divisiblePorPrimos, multiploDe4);
    }

    /**
     * Busca el primer valor repetido dentro de una muestra ya generada.
     *
     * <p>Recorre X(0) = semilla, X(1), ..., X(N) guardando dónde apareció cada valor.
     * Si X(j) ya había salido en la posición i, el ciclo empieza en i y mide j - i.
     * Si no hay repeticiones, se concluye que mu + lambda &gt; N.
     */
    public ResultadoCiclo buscarRepeticion(long semilla, List<Observacion> observaciones) {
        Map<Long, Integer> primeraAparicion = new HashMap<>();
        primeraAparicion.put(semilla, 0);
        for (Observacion obs : observaciones) {
            Integer anterior = primeraAparicion.putIfAbsent(obs.x(), obs.n());
            if (anterior != null) {
                return ResultadoCiclo.hallado(obs.n() - anterior, anterior, obs.n());
            }
        }
        return ResultadoCiclo.noHallado(observaciones.size());
    }

    /** Mide el ciclo completo, sin límite de pasos. */
    public ResultadoCiclo medirPeriodo(LongUnaryOperator transicion, long semilla) {
        return medirPeriodo(transicion, semilla, SIN_LIMITE);
    }

    /**
     * Mide lambda y mu con el algoritmo de Brent usando memoria constante.
     *
     * <p>Sirve para cualquier función de transición, tenga o no cola antes del
     * ciclo. Si la búsqueda alcanza {@code limitePasos} evaluaciones de f sin
     * cerrar el ciclo, se detiene y devuelve un resultado no encontrado.
     */
    public ResultadoCiclo medirPeriodo(LongUnaryOperator transicion, long semilla, long limitePasos) {
        // Fase 1 - longitud del ciclo (lambda). La tortuga espera fija mientras la
        // liebre avanza; si la liebre da 'potencia' pasos sin alcanzarla, la tortuga
        // salta a la posición de la liebre y la potencia se duplica. Cuando se
        // encuentran, los pasos dados desde el último salto son el período.
        long potencia = 1;
        long periodo = 1;
        long tortuga = semilla;
        long liebre = transicion.applyAsLong(semilla);
        long pasos = 1;
        while (tortuga != liebre) {
            if (pasos >= limitePasos) {
                return ResultadoCiclo.noHallado(pasos);
            }
            if (potencia == periodo) {
                tortuga = liebre;
                potencia *= 2;
                periodo = 0;
            }
            liebre = transicion.applyAsLong(liebre);
            periodo++;
            pasos++;
        }

        // Fase 2 - inicio del ciclo (mu). Dos punteros separados 'periodo' pasos
        // avanzan juntos desde la semilla; donde coinciden por primera vez está el
        // primer valor que pertenece al ciclo.
        tortuga = semilla;
        liebre = semilla;
        for (long i = 0; i < periodo; i++) {
            liebre = transicion.applyAsLong(liebre);
        }
        long inicio = 0;
        while (tortuga != liebre) {
            tortuga = transicion.applyAsLong(tortuga);
            liebre = transicion.applyAsLong(liebre);
            inicio++;
        }
        return ResultadoCiclo.hallado(periodo, inicio, pasos + periodo + 2 * inicio);
    }

    /** Factores primos distintos de {@code numero} por división de prueba. */
    private static List<Long> factoresPrimos(long numero) {
        List<Long> factores = new ArrayList<>();
        // divisor <= numero / divisor equivale a divisor^2 <= numero sin riesgo de desbordamiento.
        for (long divisor = 2; divisor <= numero / divisor; divisor += (divisor == 2 ? 1 : 2)) {
            if (numero % divisor == 0) {
                factores.add(divisor);
                while (numero % divisor == 0) {
                    numero /= divisor;
                }
            }
        }
        if (numero > 1) {
            factores.add(numero); // lo que queda es un primo mayor que la raíz
        }
        return factores;
    }

    /** Máximo común divisor por el algoritmo de Euclides. */
    private static long mcd(long x, long y) {
        while (y != 0) {
            long resto = x % y;
            x = y;
            y = resto;
        }
        return x;
    }
}
