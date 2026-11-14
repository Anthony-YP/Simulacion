package montecarlo.modelo;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

/** Resultados de Java y Python para el mismo N. */
public record FilaComparacion(
        int nPuntos,
        double piJava,
        double piPython,
        double errorJava,
        double errorPython,
        double tiempoJavaMs,
        double tiempoPythonMs) {

    public boolean mismaEstimacion() {
        return piJava == piPython;
    }

    /** Cuántas veces más rápido fue Java (tiempo Python / tiempo Java). */
    public double razonTiempos() {
        return tiempoJavaMs > 0 ? tiempoPythonMs / tiempoJavaMs : Double.POSITIVE_INFINITY;
    }

    /** Empareja los resultados de ambos lenguajes que tienen el mismo N. */
    public static List<FilaComparacion> comparar(List<ResultadoEstimacion> java, List<ResultadoEstimacion> python) {
        Map<Integer, ResultadoEstimacion> pythonPorN = python.stream()
                .collect(Collectors.toMap(ResultadoEstimacion::nPuntos, Function.identity(), (a, b) -> b));
        return java.stream()
                .filter(j -> pythonPorN.containsKey(j.nPuntos()))
                .map(j -> {
                    ResultadoEstimacion p = pythonPorN.get(j.nPuntos());
                    return new FilaComparacion(j.nPuntos(), j.piEstimado(), p.piEstimado(),
                            j.errorAbsoluto(), p.errorAbsoluto(), j.tiempoMs(), p.tiempoMs());
                })
                .toList();
    }
}
