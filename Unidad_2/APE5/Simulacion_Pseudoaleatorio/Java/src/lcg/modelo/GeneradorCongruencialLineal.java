package lcg.modelo;

import java.util.Objects;

/** Generador Congruencial Lineal mixto: X(n+1) = (a * X(n) + c) mod m. */
public final class GeneradorCongruencialLineal implements GeneradorPseudoaleatorio {

    private final ParametrosLCG parametros;
    private long estado; // X(n) del último valor generado
    private int n;       // posición n del último valor generado

    public GeneradorCongruencialLineal(ParametrosLCG parametros) {
        this.parametros = Objects.requireNonNull(parametros, "parametros");
        reiniciar();
    }

    public ParametrosLCG parametros() {
        return parametros;
    }

    @Override
    public long semilla() {
        return parametros.semilla();
    }

    @Override
    public long transicion(long x) {
        // ParametrosLCG garantiza que a*x + c cabe en un long, así que el cálculo es exacto
        // y, al ser todos los operandos no negativos, % devuelve el residuo de la fórmula.
        return (parametros.a() * x + parametros.c()) % parametros.m();
    }

    @Override
    public double normalizar(long x) {
        // La conversión a double es necesaria: x / m entre enteros daría siempre 0.
        return (double) x / parametros.m();
    }

    @Override
    public Observacion siguiente() {
        estado = transicion(estado);
        n++;
        return new Observacion(n, estado, normalizar(estado));
    }

    @Override
    public void reiniciar() {
        estado = parametros.semilla();
        n = 0;
    }
}
