package montecarlo.modelo;

/** Generador Congruencial Lineal: produce números pseudoaleatorios uniformes en [0, 1). */
public final class GeneradorCongruencialLineal {

    private final ParametrosLCG parametros;
    private final double modulo;
    private long estado;

    public GeneradorCongruencialLineal(ParametrosLCG parametros) {
        this.parametros = parametros;
        this.modulo = parametros.m();
        this.estado = parametros.semilla();
    }

    public ParametrosLCG getParametros() {
        return parametros;
    }

    /** Último estado entero X(n). */
    public long getEstado() {
        return estado;
    }

    public long siguienteEntero() {
        estado = (parametros.a() * estado + parametros.c()) % parametros.m();
        return estado;
    }

    /** Avanza un paso y devuelve U(n) = X(n) / m. */
    public double siguiente() {
        return siguienteEntero() / modulo;
    }

    public double[] generar(int cantidad) {
        if (cantidad < 0) {
            throw new IllegalArgumentException("La cantidad de números no puede ser negativa.");
        }
        double[] numeros = new double[cantidad];
        for (int i = 0; i < cantidad; i++) {
            numeros[i] = siguiente();
        }
        return numeros;
    }

    /** Vuelve a la semilla para reproducir exactamente la misma secuencia. */
    public void reiniciar() {
        estado = parametros.semilla();
    }
}
