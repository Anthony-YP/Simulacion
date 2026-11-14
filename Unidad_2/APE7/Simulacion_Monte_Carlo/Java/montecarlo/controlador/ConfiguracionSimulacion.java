package montecarlo.controlador;

import java.util.List;

import montecarlo.modelo.ParametrosLCG;

/** Parámetros de una corrida completa de la simulación. */
public record ConfiguracionSimulacion(
        List<Integer> tamanios,
        ParametrosLCG parametros,
        int repeticiones,
        boolean generarGraficos,
        int numerosMuestra,
        String lenguaje) {

    public static ConfiguracionSimulacion porDefecto() {
        return new ConfiguracionSimulacion(
                List.of(1_000, 10_000, 100_000, 1_000_000),
                ParametrosLCG.NUMERICAL_RECIPES,
                10,
                true,
                5,
                "Java");
    }
}
