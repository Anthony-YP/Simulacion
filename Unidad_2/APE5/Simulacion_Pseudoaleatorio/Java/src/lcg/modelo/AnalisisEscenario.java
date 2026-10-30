package lcg.modelo;

import java.util.List;

/**
 * Resultado de un escenario: teoría, ciclo medido y primeros valores X(0), X(1), ...
 */
public record AnalisisEscenario(
        EscenarioPeriodo escenario,
        ResultadoHullDobell hullDobell,
        ResultadoCiclo ciclo,
        List<Long> valores) {

    public AnalisisEscenario {
        valores = List.copyOf(valores);
    }
}
