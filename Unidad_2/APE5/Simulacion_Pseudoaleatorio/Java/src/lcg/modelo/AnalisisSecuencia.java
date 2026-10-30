package lcg.modelo;

/**
 * Estadística y período de una secuencia generada con ciertos parámetros.
 *
 * @param repeticion búsqueda de valores repetidos dentro de la muestra
 */
public record AnalisisSecuencia(
        ParametrosLCG parametros,
        ResumenEstadistico estadisticas,
        ResultadoHullDobell hullDobell,
        ResultadoCiclo repeticion) {
}
